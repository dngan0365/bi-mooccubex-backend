import boto3
from boto3.dynamodb.conditions import Key
from api.models.user import UserInDB
import os

dynamodb = boto3.resource("dynamodb", 
                          region_name=os.getenv("AWS_REGION", "us-east-1"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
                          )

user_table = dynamodb.Table("user")

def get_user_by_email(email: str):
    response = user_table.query(
        IndexName='email-index',  # Make sure you have a GSI on email
        KeyConditionExpression=Key('email').eq(email)
    )
    items = response.get('Items')
    if items:
        return UserInDB(**items[0])
    return None

def create_user(user: UserInDB):
    user_dict = user.dict()
    user_dict['id'] = str(user_dict['id'])  # Convert UUID to string
    user_table.put_item(Item=user_dict)