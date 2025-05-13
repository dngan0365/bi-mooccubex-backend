import boto3
import os
dynamodb = boto3.client("dynamodb", 
                        region_name="us-east-1",
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
table_name = 'user'

# Check if table exists
existing_tables = dynamodb.list_tables()["TableNames"]
if table_name in existing_tables:
    print(f"Table '{table_name}' already exists.")
else:
    response = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'},  # For GSI
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'email-index',
                'KeySchema': [
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
                # 🚫 REMOVE ProvisionedThroughput here
            }
        ],
        BillingMode='PAY_PER_REQUEST',  # On-demand billing
    )

    print("Creating table...")
    dynamodb.get_waiter('table_exists').wait(TableName=table_name)
    print("Table created.")
