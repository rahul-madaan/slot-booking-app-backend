from datetime import datetime
import boto3
import os
from boto3.dynamodb.conditions import Key
from botocore.config import Config
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel
import csv

from app import cypher

router = APIRouter()

load_dotenv()
s3 = boto3.resource(service_name='s3')
s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
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


class SetAttendanceStatus(BaseModel):
    value: str


class NetID(BaseModel):
    net_id: str


class Login(BaseModel):
    net_id: str
    password: str


class VerifyLogin(BaseModel):
    encrypted_net_id: str
    encrypted_net_id_len: str


@router.post("/login")
async def login(request_body: Login):
    if request_body.net_id == "sonia.khetarpaul@snu.edu.in":
        if request_body.password == "strongpassword":
            encryptedNetID = cypher.encrypt(request_body.net_id)
            net_id_len = cypher.encrypt(str(len(request_body.net_id)))
            return {"status": "LOGIN_SUCCESSFUL",
                    "encrypted_net_id": encryptedNetID,
                    "net_id_len": net_id_len}
        else:
            return {"status": "INCORRECT_PASSWORD"}

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
                if decMessage == "sonia.khetarpaul@snu.edu.in":
                    return {'loginSuccess': 1,
                            'user_net_id': decMessage}
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

    location_status = check_location(request_body.latitude, request_body.longitude)
    if location_status['status'] != "LOCATION_INSIDE_B315":
        print(location_status)
        return location_status

    attendance_table.put_item(
        Item={
            'net_id': request_body.net_id,
            'IP_address': request_body.IP_address,
            'browser_fingerprint': request_body.browser_fingerprint,
            'date': str(datetime.now())[:10],
            'time': str(datetime.now())[11:19]
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


@router.get("/check-attendance")
async def check_attendance():
    result = (attendance_table.query(IndexName="date-index",
                                     KeyConditionExpression=Key('date').eq(str(datetime.now())[:10])))
    present = []
    final_present = []
    if len(result["Items"]) == 0:
        return {"status": "NO ONE MARKED YET",
                "present": []}
    else:
        for item in result["Items"]:
            present.append(item['net_id'])
        for net_id in present:
            result = student_details_table.query(KeyConditionExpression=Key('net_id').eq(net_id))['Items'][0]
            details = {}
            details['net_id'] = net_id
            details['roll_number'] = result['roll_number']
            details['name'] = result['first_name'] + " " + result['last_name']
            final_present.append(details)

        return {"status": "marked",
                "present": final_present}


@router.get("/check-attendance-status")
async def check_attendance_status():
    result = flags_table.query(KeyConditionExpression=Key('key').eq("attendance_initiated"))
    if result["Items"][0]["value"] == 'false':
        return {"status": 0}
    return {"status": 1}


@router.post("/set-attendance-status")
async def set_attendance_status(request_body: SetAttendanceStatus):
    if request_body.value == "true":
        flags_table.put_item(Item={"key": 'attendance_initiated', "value": 'true'})
    else:
        flags_table.put_item(Item={"key": 'attendance_initiated', "value": 'false'})
    return {"status": "set complete"}


@router.post("/search-student")
async def search_student(request_body: NetID):
    result = student_details_table.query(KeyConditionExpression=Key('net_id').eq(request_body.net_id))
    if len(result['Items']) == 0:
        return {"status": "NET_ID_NOT_FOUND"}
    else:
        result_attendance = attendance_table.query(IndexName="date-index",
                                                   KeyConditionExpression=Key('date').eq(str(datetime.now())[:10]))
        for item in result_attendance["Items"]:
            if item["net_id"] == request_body.net_id:
                result['Items'][0]["attendance"] = "PRESENT"
                return result['Items'][0]
        result["Items"][0]["attendance"] = "ABSENT"
        return result['Items'][0]


@router.post("/mark-attendance-override")
async def mark_attendance_override(request_body: NetID):
    attendance_table.put_item(
        Item={
            'net_id': request_body.net_id,
            'IP_address': "0.0.0.0",
            'browser_fingerprint': "0000000000000000",
            'date': str(datetime.now())[:10],
            'time': str(datetime.now())[11:19]
        })
    return {"status": "ATTENDANCE_MARKED_SUCCESSFULLY"}


@router.get("/download-attendance")
async def download_attendance():
    BUCKET = "fastapi-slot-booking"
    result = (attendance_table.query(IndexName="date-index",
                                     KeyConditionExpression=Key('date').eq(str(datetime.now())[:10])))
    details = student_details_table.scan()['Items']
    present = []
    for item in result['Items']:
        present.append(item['net_id'])
    for i in range(len(present)):
        for details_net_id in details:
            if present[i] == details_net_id["net_id"]:
                present[i] = details_net_id["roll_number"]
                break
    student_details = []
    with open('app/sample_attendance.csv') as file:
        csvFile = csv.reader(file)
        for lines in csvFile:
            student_details.append(lines)

    student_details = student_details[1:]

    for row in student_details:
        if row[0] in present:
            row[2] = 'Present'

    text = 'Student Id, Student Name, Attendance Status \n'
    for row in student_details:
        line = row[0] + "," + row[1] + "," + row[2] + "\n"
        text += line
    with open("/tmp/attendance " + str(datetime.now())[:10] + ".csv", "w") as text_file:
        text_file.write(text)

    s3.Bucket(BUCKET).upload_file("/tmp/attendance " + str(datetime.now())[:10] + ".csv",
                                  "DBMS_attendance/attendance " + str(datetime.now())[:10] + ".csv")
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': 'fastapi-slot-booking',
                'Key': "DBMS_attendance/attendance " + str(datetime.now())[:10] + ".csv"},
        ExpiresIn=60,
    )
    if os.path.exists("/tmp/attendance " + str(datetime.now())[:10] + ".csv"):
        os.remove("/tmp/attendance " + str(datetime.now())[:10] + ".csv")
    return {"url": url}
