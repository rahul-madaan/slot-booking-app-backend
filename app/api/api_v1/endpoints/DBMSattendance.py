from datetime import datetime, timedelta
import boto3
import os

from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"))

product_table = dynamo_resource.Table('dbms-student-details')


class MarkAttendance(BaseModel):
    net_id: str
    IP_address: str
    browser_fingerprint: str
    latitude: str
    longitude: str


class Login(BaseModel):
    net_id: str
    password: str


@router.post("/login")
async def login(request_body: Login):
    result = product_table.query(KeyConditionExpression=Key('net_id').eq("am795"))
    if len(result["Items"]) == 0:
        return {"status": "USER_NOT_REGISTERED"}
    else:
        student_details = result["Items"][0]
        if(student_details['roll_number'] == request_body.password):
            return {"status": "LOGIN_SUCCESSFUL"}
        else:
            return {"status": "PASSWORD_DOES_NOT_MATCH"}


@router.post("/mark-attendance")
async def mark_attendance(request_body: MarkAttendance):
    return request_body
