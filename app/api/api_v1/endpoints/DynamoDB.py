import boto3
import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"),
                                 aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                                 aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

product_table = dynamo_resource.Table('slot-booking-app')


class MarkAttendance(BaseModel):
    email_id: str
    IP_address: str


@router.post("/mark-attendance")
async def login(request_body: MarkAttendance):
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
                'IP_address': request_body.IP_address
            })
        return "Added record successfully"
    except ClientError as err:
        return {"Error": "Couldn't load data into table",
                "error_message": err}
