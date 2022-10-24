from datetime import datetime, timedelta
import boto3
import os

from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

from app import cypher

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"))

student_details_table = dynamo_resource.Table('dbms-student-details')
attendance_table = dynamo_resource.Table('dbms-attendance')
flags_table = dynamo_resource.Table('flags')


class MarkAttendance(BaseModel):
    net_id: str
    IP_address: str
    browser_fingerprint: str
    latitude: str
    longitude: str


class Login(BaseModel):
    net_id: str
    password: str


class VerifyLogin(BaseModel):
    encrypted_net_id: str
    encrypted_net_id_len: str


@router.post("/login")
async def login(request_body: Login):
    result = student_details_table.query(KeyConditionExpression=Key('net_id').eq(request_body.net_id))
    if len(result["Items"]) == 0:
        return {"status": "USER_NOT_REGISTERED"}
    else:
        student_details = result["Items"][0]
        if student_details['roll_number'] == request_body.password:
            encryptedNetID = cypher.encrypt(request_body.net_id)
            net_id_len = cypher.encrypt(str(len(request_body.net_id)))
            return {"status": "LOGIN_SUCCESSFUL",
                    "encrypted_net_id": encryptedNetID,
                    "net_id_len": net_id_len}
        else:
            return {"status": "PASSWORD_DOES_NOT_MATCH"}


@router.post("/verify-login")
async def verify_login(request_body: VerifyLogin):
    try:
        if 5 * int(cypher.decrypt(str(request_body.encrypted_net_id_len))) == len(request_body.encrypted_net_id):
            try:
                decMessage = cypher.decrypt(request_body.encrypted_net_id)
                result = student_details_table.query(KeyConditionExpression=Key('net_id').eq(decMessage))['Items'][0]
                name = result['first_name'] + " " + result["last_name"]
                roll_number = result['roll_number']
                return {'loginSuccess': 1,
                        'user_net_id': decMessage,
                        'name': name,
                        'roll_number': roll_number}
            except Exception as e:
                print(e)
                return {'loginSuccess': 0,
                        'user_net_id': ""}
        else:
            return {'loginSuccess': 0,
                    'user_net_id': ""}
    except Exception as e:
        print(e)
        return {'loginSuccess': 0,
                'user_net_id': ""}


@router.post("/mark-attendance")
async def mark_attendance(request_body: MarkAttendance):
    already_marked_status = check_already_marked(request_body.net_id)
    if already_marked_status["status"] == 'ALREADY_MARKED':
        print(already_marked_status)
        return already_marked_status

    attendance_initiated_status = check_attendance_initiated_status()
    if attendance_initiated_status['status'] == "ATTENDANCE_NOT_INITIATED":
        return attendance_initiated_status

    bp_status = check_browser_fingerprint(request_body.browser_fingerprint)
    if bp_status['status'] != "VERIFIED":
        print(bp_status)
        return bp_status

    ip_status = check_IP_address(request_body.IP_address)
    if ip_status['status'] != "VERIFIED":
        print(ip_status)
        return ip_status

    # location_status = check_location(request_body.latitude, request_body.longitude)
    # if location_status['status'] != "LOCATION_INSIDE_B315":
    #     print(location_status)
    #     return location_status

    attendance_table.put_item(
        Item={
            'net_id': request_body.net_id,
            'IP_address': request_body.IP_address,
            'browser_fingerprint': request_body.browser_fingerprint,
            'date': str(datetime.now())[:10],
            'time': str(datetime.now())[10:19]
        })
    print({"status": "ATTENDANCE_MARKED_SUCCESSFULLY"})
    return {"status": "ATTENDANCE_MARKED_SUCCESSFULLY"}


def check_attendance_initiated_status():
    result = flags_table.query(KeyConditionExpression=Key('key').eq("attendance_initiated"))
    if result["Items"][0]["value"] == 'false':
        return {"status": "ATTENDANCE_NOT_INITIATED"}
    return {"status": "ATTENDANCE_INITIATED"}

def check_already_marked(net_id: str):
    result = attendance_table.query(KeyConditionExpression=Key('net_id').eq(net_id))
    if len(result["Items"]) != 0:
        for i in range(len(result["Items"])):
            if result["Items"][i]["date"] == str(datetime.now())[:10]:
                return {"status": "ALREADY_MARKED"}
    return {"status": "ATTENDANCE_NOT_YET_MARKED"}


def check_browser_fingerprint(browser_fingerprint: str):
    if browser_fingerprint == "":
        return {"status": "CANNOT_RECORD_BROWSER_FINGERPRINT"}

    result = (attendance_table.query(IndexName="browser_fingerprint-index",
                                     KeyConditionExpression=Key('browser_fingerprint').eq(browser_fingerprint))[
        'Items'])
    for i in range(len(result)):
        if result[i]['date'] == str(datetime.now())[:10]:
            return {"status": "SAME_DEVICE"}
    return {"status": 'VERIFIED'}


def check_IP_address(IP_address: str):
    if IP_address == "":
        return {"status": "CANNOT_RECORD_IP_ADDRESS"}

    result = (attendance_table.query(IndexName="IP_address-index",
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
    if float(os.getenv("MAX_LATITUDE_B315")) >= latitude >= float(os.getenv("MIN_LATITUDE_B315")) and float(os.getenv(
            "MAX_LONGITUDE_B315")) >= longitude >= float(os.getenv("MIN_LONGITUDE_B315")):
        return {"status": "LOCATION_INSIDE_B315"}
    else:
        return {"status": "LOCATION_OUTSIDE_B315"}
