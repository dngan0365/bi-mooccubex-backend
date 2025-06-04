import boto3
import time
import json
import os
import logging
import pandas as pd


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
        if path == "/api/user-course-info" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            user_id = event.get("queryStringParameters", {}).get("user_id")
            query = f"""
                SELECT DISTINCT user_id, school, user_month, user_year, end_month, end_year
                FROM full_phase1
                WHERE course_id = '{course_id}' AND user_id = '{user_id}'
                ORDER BY user_year, user_month
                limit 1
            """
            user_info = run_athena_query(query)

            query = f"""
                SELECT COUNT(*) AS exercise_count
                FROM exercise
                WHERE exercise_submit_date_max IS NOT NULL AND course_id = '{course_id}' AND user_id = '{user_id}'
            """
            user_exercises = run_athena_query(query)
            
            if course_id.startswith("C_"):
                course = int(course_id[2:])

            query = f"""
                SELECT COUNT(*) AS video_count
                FROM video
                WHERE year >= 2019 AND course_id = {course} AND user_id = '{user_id}'
            """

            user_video = run_athena_query(query)

            query = f"""
                SELECT DISTINCT user_id, course_id, assignment_score, final_exam_score, video_score, total_score
                FROM score_proportion
                WHERE course_id = '{course_id}' AND user_id = '{user_id}'
                LIMIT 1
            """
            user_comments = run_athena_query(query)

            data = {
                "user_info": user_info,
                "user_exercises": user_exercises,
                "user_video": user_video,
                "user_comments": user_comments
            }

        elif path == "/api/user-course-score-proportion" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            user_id = event.get("queryStringParameters", {}).get("user_id")
            query = f"""
                SELECT DISTINCT user_id, course_id, assignment_score, final_exam_score, video_score, total_score
                FROM score_proportion
                WHERE course_id = '{course_id}' AND user_id = '{user_id}'
                LIMIT 1
            """
            data = run_athena_query(query)

        elif path == "/api/user-course-behaviour" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            user_id = event.get("queryStringParameters", {}).get("user_id")
            query = f"""
                SELECT 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)) AS year,
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE)) AS month,
                COUNT(*) AS exercise_count
                FROM exercise
                WHERE exercise_submit_date_max IS NOT NULL AND course_id = '{course_id}' AND user_id = '{user_id}'
                GROUP BY 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)),
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE))
                ORDER BY 
                YEAR(TRY_CAST(exercise_submit_date_max AS DATE)),
                MONTH(TRY_CAST(exercise_submit_date_max AS DATE));
            """
            user_exercises = run_athena_query(query)
            
            if course_id.startswith("C_"):
                course = int(course_id[2:])

            query = f"""
                SELECT 
                year,
                month,
                COUNT(*) AS video_count
                FROM video
                WHERE year >= 2019 AND course_id = {course} AND user_id = '{user_id}'
                GROUP BY year, month
                ORDER BY year, month;
            """

            user_video = run_athena_query(query)

            data = {
                "user_video": user_video,
                "user_exercises": user_exercises
            }

        elif path == "/api/user-course-predict" and method == "GET":
            course_id = event.get("queryStringParameters", {}).get("course_id")
            user_id = event.get("queryStringParameters", {}).get("user_id")

            import pandas as pd
            import pickle
            import io
            import os

            s3 = boto3.client("s3")
            s3_bucket = 'mooccubex-datalake'
            s3_prefix = 'tools/random-forest/'

            # Load school_mapping.pkl from S3
            school_map_obj = s3.get_object(Bucket=s3_bucket, Key=f"tools/school_mapping.pkl")
            school_map = pickle.loads(school_map_obj['Body'].read())

            # Store all phase results
            results = []

            for phase in range(1, 5):
                query = f"""
                    SELECT *
                    FROM phase{phase}
                    WHERE user_id = '{user_id}' AND course_id = '{course_id}'
                    LIMIT 1
                """
                rows = run_athena_query(query)
                if not rows:
                    continue  # Skip if no data for this phase

                df = pd.DataFrame(rows)
                if df.empty:
                    continue

                # --- PREPROCESS ---
                df['school'] = df['school'].map(school_map).fillna(0).astype(int)

                # Drop non-feature columns
                non_features = ['total_score', 'label', 'label_encoded']
                feature_columns = [col for col in df.columns if col not in non_features]
                features = df[feature_columns]

                # Handle potential string-type numeric fields (example for phase 2)
                for col in features.columns:
                    if features[col].dtype == 'object':
                        try:
                            features[col] = pd.to_numeric(features[col], errors='coerce')
                        except Exception:
                            pass
                features.fillna(0, inplace=True)

                # --- LOAD SCALER ---
                scaler_key = f"{s3_prefix}best_scaler_no_sample_phase{phase}.pkl"
                scaler_obj = s3.get_object(Bucket=s3_bucket, Key=scaler_key)
                scaler = pickle.loads(scaler_obj['Body'].read())

                X_scaled = scaler.transform(features)

                # --- LOAD MODEL ---
                model_key = f"{s3_prefix}best_model_no_sample_phase{phase}.pkl"
                model_obj = s3.get_object(Bucket=s3_bucket, Key=model_key)
                model = pickle.loads(model_obj['Body'].read())

                # --- PREDICT ---
                y_pred = model.predict(X_scaled)
                y_true = df.get('label_encoded', [None])[0]

                output = features.copy()
                output['predicted_label'] = y_pred[0]
                output['true_label'] = y_true

                results.append({
                    "phase": phase,
                    "data": output.to_dict(orient="records")[0]
                })

            



        
            

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