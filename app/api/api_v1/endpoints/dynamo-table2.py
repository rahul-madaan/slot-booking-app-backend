import boto3
import os
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from fastapi import APIRouter

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"))

product_table = dynamo_resource.Table('slot-app')

product_table.put_item(
    Item={"email_id": "lm222@snu.edu.in",
          "date": str(datetime.now()+timedelta(days=2))[:10],
          "IP_address": "1.2.3.4",
          "browser_fingerprint": "lol0"
          }
)

result = (
    product_table.query(KeyConditionExpression=Key('email_id').eq("lm222@snu.edu.in"))['Items'])


result = (product_table.query(IndexName="date-index", KeyConditionExpression=Key('date').eq(str(datetime.now()+timedelta(days=2))[:10]))['Items'])

# product_table.scan(FilterExpression=Key('attendance_record').eq("2022-10-14"))['Items'])
print(result)

