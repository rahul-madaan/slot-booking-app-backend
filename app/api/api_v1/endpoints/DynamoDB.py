from datetime import datetime, timedelta
import boto3
import os

from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"))

product_table = dynamo_resource.Table('slot-app')


class MarkAttendance(BaseModel):
    email_id: str
    IP_address: str
    browser_fingerprint: str


@router.post("/mark-attendance")
async def mark_attendance(request_body: MarkAttendance):
    try:
        ## BATCH UPDATE
        # with product_table.batch_writer() as writer:
        #     writer.put_item(Item={
        #         'email_id': request_body.email_id,
        #         'IP_address': request_body.IP_address
        #     }
        #     )
        product_table.put_item(
            Item={
                'email_id': request_body.email_id,
                'IP_address': request_body.IP_address,
                'browser_fingerprint': request_body.browser_fingerprint,
                'date': str(datetime.now())[:10],
                'time': str(datetime.now())[10:19]
            })
        return "Added record successfully"
    except ClientError as err:
        return {"Error": "Couldn't load data into table",
                "error_message": err}


@router.get("/check-browser-fingerprint")
async def check_browser_fingerprint(browser_fingerprint: str):
    if browser_fingerprint == "":
        return {"status": "CANNOT_RECORD_BROWSER_FINGERPRINT"}

    result = (product_table.query(IndexName="browser_fingerprint-index",
                                  KeyConditionExpression=Key('browser_fingerprint').eq(browser_fingerprint))['Items'])
    for i in range(len(result)):
        if result[i]['date'] == str(datetime.now())[:10]:
            return {"status": "SAME_DEVICE"}
    return {"status": 'VERIFIED'}


@router.get("/check-IP_address")
async def check_IP_address(IP_address: str):
    if IP_address == "":
        return {"status": "CANNOT_RECORD_IP_ADDRESS"}

    result = (product_table.query(IndexName="IP_address-index",
                                  KeyConditionExpression=Key('IP_address').eq(IP_address))['Items'])
    for i in range(len(result)):
        if result[i]['date'] == str(datetime.now())[:10]:
            return {"status": "SAME_DEVICE"}
    return {"status": 'VERIFIED'}
