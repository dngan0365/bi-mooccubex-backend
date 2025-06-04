import boto3
import time
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment Variables
DATABASE = os.environ.get('DATABASE', 'analyticsworkshopdb')
S3_OUTPUT = "s3://mooccubex-datalake/query_results/"

athena = boto3.client("athena")

def run_athena_query(query):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": S3_OUTPUT}
    )
    execution_id = response["QueryExecutionId"]
    logger.info(f"QueryExecutionId: {execution_id}")

    while True:
        status = athena.get_query_execution(QueryExecutionId=execution_id)
        state = status["QueryExecution"]["Status"]["State"]
        logger.info(f"Athena query state: {state}")
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        reason = status["QueryExecution"]["Status"].get("StateChangeReason", "Unknown reason")
        logger.error(f"Query failed. Reason: {reason}")
        raise Exception(f"Athena query failed: {state}")

    results = athena.get_query_results(QueryExecutionId=execution_id)
    headers = [col["VarCharValue"] for col in results["ResultSet"]["Rows"][0]["Data"]]
    rows = results["ResultSet"]["Rows"][1:]

    data = []
    for row in rows:
        values = [col.get("VarCharValue", None) for col in row["Data"]]
        data.append(dict(zip(headers, values)))
    return data

def lambda_handler(event, context):
    logger.info(json.dumps(event))
    path = event.get("path", "")
    method = event.get("httpMethod", "")
    logger.info(f"Processing request: {method} {path}")

    try:
        if path == "/api/top-courses" and method == "GET":
            query = """
                SELECT 
                    f.course_id, 
                    c.name, 
                    COUNT(*) AS user_count
                FROM 
                    full_phase1 f
                JOIN 
                    course_info c ON f.course_id = c.course_id
                GROUP BY 
                    f.course_id, c.name
                ORDER BY 
                    user_count DESC
                LIMIT 5;
            """
            data = run_athena_query(query)

        elif path == "/api/monthly-users" and method == "GET":
            query = """
                SELECT 
                  user_year AS year,
                  user_month AS month,
                  COUNT(DISTINCT user_id) AS num_users
                FROM full_phase1
                WHERE user_year >= 2019
                GROUP BY user_year, user_month
                ORDER BY user_year, user_month;
            """
            data = run_athena_query(query)

        elif path == "/api/yearly-users" and method == "GET":
            query = """
                SELECT 
                  user_year AS year,
                  COUNT(DISTINCT user_id) AS num_users
                FROM full_phase1
                WHERE user_year >= 2019
                GROUP BY user_year
                ORDER BY user_year;
            """
            data = run_athena_query(query)

        elif path == "/api/summary-stats" and method == "GET":
            query = """
                SELECT
                  (SELECT COUNT(DISTINCT user_id) FROM full_phase1) AS total_users,
                  (SELECT COUNT(DISTINCT course_id) FROM full_phase1) AS total_courses,
                  (SELECT COUNT(DISTINCT course_id) 
                   FROM full_phase1
                   WHERE (user_year > 2020 OR (user_year = 2020 AND user_month >= 7))
                  ) AS courses_since_july_2020,
                  (SELECT COUNT(DISTINCT user_id) 
                   FROM full_phase1
                   WHERE user_year = 2020
                  ) AS users_in_2020;
            """
            data = run_athena_query(query)

        elif path == "/api/label-distribution" and method == "GET":
            query = """
                SELECT 
                  label,
                  COUNT(*) AS num_users
                FROM full_phase1
                WHERE label IN ('A', 'B', 'C', 'D','E')
                  AND (
                    end_year = 2019 
                    OR (end_year = 2021 AND end_month < 7)
                  )
                GROUP BY label
                ORDER BY num_users DESC;
            """
            data = run_athena_query(query)
            
        elif path == "/api/course-enrollments" and method == "GET":
            query = """
                SELECT 
                    p.course_id,
                    c.name,
                    p.school,
                    c.start_date,
                    c.end_date,
                    COUNT(DISTINCT p.user_id) AS user_count
                FROM 
                    phase1 p
                JOIN 
                    course_info c ON p.course_id = c.course_id
                GROUP BY 
                    p.course_id, c.name, p.school, c.start_date, c.end_date
                ORDER BY 
                    user_count DESC
                LIMIT 100;
            """
            data = run_athena_query(query)

        elif path.startswith("/api/course/") and method == "GET":
            course_id = path.split("/")[-1]
            query = query = f"""
                SELECT 
                    c.course_id,
                    c.name,
                    c.start_date,
                    c.end_date,
                    c.duration_days,
                    c.certificate,
                    c.assignment,
                    c.exam,
                    c.video,
                    c.video_count,
                    c.exercise_count,
                    c.chapter_count
                FROM course_info c
                WHERE c.course_id = '{course_id}'
                LIMIT 1
            """
            data = run_athena_query(query)
        elif path == "/api/search-labels" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            if not course_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing course_id"})
                }

            query = f"""
                SELECT 
                    label,
                    COUNT(*) AS count
                FROM phase1
                WHERE course_id = '{course_id}'
                  AND label IN ('A', 'B', 'C', 'D', 'E')
                GROUP BY label
                ORDER BY count DESC;
            """
            data = run_athena_query(query)
        elif path == "/api/course-video-count" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            if not course_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing course_id"})
                }
            if course_id.startswith("C_"):
                course_id = int(course_id[2:])

            query = f"""
                SELECT 
                year,
                month,
                COUNT(*) AS video_count
                FROM video
                WHERE year >= 2019 AND course_id = {course_id}
                GROUP BY year, month
                ORDER BY year, month;
            """
            data = run_athena_query(query)
        elif path == "/api/course-exercise-count" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            if not course_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing course_id"})
                }

            query = f"""
                SELECT 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)) AS year,
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE)) AS month,
                COUNT(*) AS exercise_count
                FROM exercise
                WHERE exercise_submit_date_max IS NOT NULL AND course_id = '{course_id}'
                GROUP BY 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)),
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE))
                ORDER BY 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)),
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE));
            """
            data = run_athena_query(query)
        
        elif path == "/api/course-comment-reply-sentiment" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            if not course_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing course_id"})
                }

            # Query comments sentiment (no course_id filter as per your SQL)
            comment_query = f"""
                SELECT
                    sentiment_label,
                    YEAR(TRY_CAST(create_time AS TIMESTAMP)) AS year,
                    MONTH(TRY_CAST(create_time AS TIMESTAMP)) AS month,
                    COUNT(*) AS comment_count
                FROM comment
                WHERE course_id = '{course_id}'
                GROUP BY
                    sentiment_label,
                    YEAR(TRY_CAST(create_time AS TIMESTAMP)),
                    MONTH(TRY_CAST(create_time AS TIMESTAMP))
                ORDER BY
                    sentiment_label,
                    year,
                    month;

            """
            comment_data = run_athena_query(comment_query)

            # Query replies sentiment filtered by course_id
            reply_query = f"""
                SELECT
                    sentiment_label,
                    YEAR(TRY_CAST(create_time AS TIMESTAMP)) AS year,
                    MONTH(TRY_CAST(create_time AS TIMESTAMP)) AS month,
                    COUNT(*) AS reply_count
                FROM reply
                WHERE course_id = '{course_id}'
                GROUP BY
                    sentiment_label,
                    YEAR(TRY_CAST(create_time AS TIMESTAMP)),
                    MONTH(TRY_CAST(create_time AS TIMESTAMP))
                ORDER BY
                    sentiment_label,
                    year,
                    month
            """
            reply_data = run_athena_query(reply_query)

            data = {
                "comments": comment_data,
                "replies": reply_data
            }

        elif path == "/api/course-users" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            if not course_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Missing course_id"})
                }

            query = f"""
                SELECT DISTINCT user_id, school, user_month, user_year
                FROM full_phase1
                WHERE course_id = '{course_id}'
                limit 100
            """

            data = run_athena_query(query)

        



        else:
            logger.warning("404 Not Found: Path or method mismatch.")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Not Found"})
            }

        logger.info(f"Returning successful response: {json.dumps(data)}")
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(data)
        }

    
    

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
