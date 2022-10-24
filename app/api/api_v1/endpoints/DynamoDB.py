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

product_table = dynamo_resource.Table('slot-app')


class MarkAttendance(BaseModel):
    email_id: str
    IP_address: str
    browser_fingerprint: str
    latitude: str
    longitude: str


@router.post("/mark-attendance")
async def mark_attendance(request_body: MarkAttendance):
    print(request_body)
    bp_status = check_browser_fingerprint(request_body.browser_fingerprint)
    if bp_status['status'] != "VERIFIED":
        print(bp_status)
        return bp_status

    ip_status = check_IP_address(request_body.IP_address)
    if ip_status['status'] != "VERIFIED":
        print(ip_status)
        return ip_status

    # location_status = check_location(request_body.latitude, request_body.longitude)
    # if location_status['status'] != "LOCATION_INSIDE_GYM":
    #     print(location_status)
    #     return location_status

    product_table.put_item(
        Item={
            'email_id': request_body.email_id,
            'IP_address': request_body.IP_address,
            'browser_fingerprint': request_body.browser_fingerprint,
            'date': str(datetime.now())[:10],
            'time': str(datetime.now())[10:19]
        })
    print({"status": "ATTENDANCE_MARKED_SUCCESSFULLY"})
    return {"status": "ATTENDANCE_MARKED_SUCCESSFULLY"}


def check_browser_fingerprint(browser_fingerprint: str):
    if browser_fingerprint == "":
        return {"status": "CANNOT_RECORD_BROWSER_FINGERPRINT"}

    result = (product_table.query(IndexName="browser_fingerprint-index",
                                  KeyConditionExpression=Key('browser_fingerprint').eq(browser_fingerprint))['Items'])
    for i in range(len(result)):
        if result[i]['date'] == str(datetime.now())[:10]:
            return {"status": "SAME_DEVICE"}
    return {"status": 'VERIFIED'}


def check_IP_address(IP_address: str):
    if IP_address == "":
        return {"status": "CANNOT_RECORD_IP_ADDRESS"}

    result = (product_table.query(IndexName="IP_address-index",
                                  KeyConditionExpression=Key('IP_address').eq(IP_address))['Items'])
    for i in range(len(result)):
        if result[i]['date'] == str(datetime.now())[:10]:
            return {"status": "SAME_DEVICE"}
    return {"status": 'VERIFIED'}


def check_location(latitude: str, longitude: str):
    latitude = float(latitude)
    longitude = float(longitude)
    if latitude == 0 or longitude == 0:
        return {"status": "UNABLE_TO_COLLECT_LOCATION"}
    if float(os.getenv("MAX_LATITUDE")) >= latitude >= float(os.getenv("MIN_LATITUDE")) and float(os.getenv(
            "MAX_LONGITUDE")) >= longitude >= float(os.getenv("MIN_LONGITUDE")):
        return {"status": "LOCATION_INSIDE_GYM"}
    else:
        return {"status": "LOCATION_OUTSIDE_GYM"}
