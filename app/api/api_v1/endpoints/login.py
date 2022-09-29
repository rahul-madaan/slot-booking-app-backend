from fastapi import APIRouter
import os
import mysql.connector
from dotenv import load_dotenv
from pydantic import BaseModel
from app import cypher
from datetime import datetime, timedelta

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

mycursor = mydb.cursor()
router = APIRouter()


class LoginUser(BaseModel):
    email_ID: str
    password: str


class RegisterUser(BaseModel):
    name: str
    phone_number: str
    email_id: str
    password: str


class VerifyLogin(BaseModel):
    encrypted_email_ID: str
    encrypted_email_ID_len: str


class ReserveSlot(BaseModel):
    email_id: str
    days_code: str
    slot_number: int


class ConfirmReservedSlot(BaseModel):
    email_id: str
    days_code: str
    slot_number: int


class UserSlotDetails(BaseModel):
    email_id: str


class LeaveReservedSlot(BaseModel):
    email_ID: str


# localhost:8000/api/v1 = default
@router.post("/login")
async def login(request_body: LoginUser):
    mycursor.execute("SELECT email_ID, password FROM user")
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    for credentials in result:
        if request_body.email_ID == credentials['email_ID']:
            if request_body.password == credentials['password']:
                encryptedEmail = cypher.encrypt(request_body.email_ID)
                email_len = cypher.encrypt(str(len(request_body.email_ID)))
                return {'statusCode': 0, 'message': 'Login Successful', 'encrypted_emailID': encryptedEmail,
                        'email_len': email_len}
            else:
                return {'statusCode': 1, 'message': 'Password does not match'}
    else:
        return {'statusCode': 2, 'message': 'User not registered'}


@router.post("/register")
async def login(request_body: RegisterUser):
    mycursor.execute("SELECT email_id FROM user WHERE email_id=\"{}\"".format(request_body.email_id))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    if len(result) != 0:
        return {"status": "User already registered!"}

    mycursor.execute(
        "INSERT INTO user (name, phone_number, email_id, password) VALUES (\"{}\", \"{}\", \"{}\", \"{}\")".format(
            request_body.name, request_body.phone_number, request_body.email_id, request_body.password))
    mydb.commit()
    return {"status": "User registered successfully!"}


@router.post("/verify-login")
async def verify_login(request_body: VerifyLogin):
    try:
        if 5 * int(cypher.decrypt(str(request_body.encrypted_email_ID_len))) == len(request_body.encrypted_email_ID):
            try:
                decMessage = cypher.decrypt(request_body.encrypted_email_ID)
                # add database check for user existence
                return {'loginSuccess': 1,
                        'user_emailID': decMessage}
            except Exception as e:
                print(e)
                return {'loginSuccess': 0,
                        'user_emailID': ""}
        else:
            return {'loginSuccess': 0,
                    'user_emailID': ""}
    except Exception as e:
        print(e)
        return {'loginSuccess': 0,
                'user_emailID': ""}


@router.post("/reserve-slot")
async def reserve_slot(request_body: ReserveSlot):
    mycursor.execute(
        "SELECT email_id,booking_status  FROM slot".format(request_body.days_code, request_body.slot_number))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    for slot in result:
        if slot['email_id'] == request_body.email_id and slot['booking_status'] == "BOOKED":
            return {"Status": "1 slot already booked"}
    mycursor.execute("SELECT * FROM slot WHERE days_code=\"{}\" AND slot_number = {}".format(request_body.days_code,
                                                                                             request_body.slot_number + 1))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    if len(result) < int(os.getenv("TOTAL_SLOTS_PER_BATCH")):
        mycursor.execute(
            "INSERT INTO slot (email_id, slot_number, days_code, booking_status) VALUES (\"{}\",{},\"{}\",\"TEMP_BOOKED\")".format(
                request_body.email_id, request_body.slot_number + 1, request_body.days_code))
        mydb.commit()
        return {"Status": "TEMP_BOOKED"}
    else:
        return {"Status": "ALREADY_FULL"}


@router.get("/available-slots/{days_code}")
async def available_slots(days_code):
    mycursor.execute("DELETE FROM slot WHERE booking_status = \"TEMP_BOOKED\" AND booking_time < \"{}\"".format(
        str(datetime.now() - timedelta(minutes=15))[:19]))
    mydb.commit()
    mycursor.execute("SELECT * FROM slot WHERE days_code=\"{}\"".format(days_code))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    available_slots = [0] * 8
    total_slots = int(os.getenv("TOTAL_SLOTS_PER_BATCH"))
    for slot_detail in result:
        slot_number = slot_detail["slot_number"]
        available_slots[slot_number - 1] += 1
    for i in range(len(available_slots)):
        available_slots[i] = total_slots - available_slots[i]

    return {"available_slots": available_slots}


@router.post("/leave-reserved-slot")
async def leave_reserved_slot(request_body: LeaveReservedSlot):
    try:
        mycursor.execute(
            "DELETE FROM slot WHERE email_id = \"{}\" AND booking_status=\"TEMP_BOOKED\"".format(request_body.email_ID))
        mydb.commit()
        return {"status": "Successfully unreserved slot if already reserved"}
    except:
        return {"status": "unable to unreserve slot booked by user"}


@router.post("/confirm-reserved-slot")
async def leave_reserved_slot(request_body: ConfirmReservedSlot):
    mycursor.execute(
        "SELECT * FROM slot WHERE email_id=\"{}\" AND days_code=\"{}\" AND slot_number={} AND booking_status=\"TEMP_BOOKED\"".format(
            request_body.email_id, request_body.days_code, request_body.slot_number + 1))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    if len(result) == 1:
        mycursor.execute(
            "UPDATE slot SET booking_status=\"BOOKED\" WHERE email_id=\"{}\" AND days_code=\"{}\" AND slot_number={} AND booking_status=\"TEMP_BOOKED\"".format(
                request_body.email_id, request_body.days_code, request_body.slot_number + 1))
        mydb.commit()
        return {"status": "Booked slot successfully"}
    else:
        return {"status": "15 minutes expired, book another slot"}


@router.post("/fetch-user-slot-details")
async def fetch_user_slot_details(request_body: UserSlotDetails):
    print(request_body.email_id)
    if request_body.email_id == "":
        return {"status": "Email field is empty"}
    mycursor.execute(
        "SELECT * FROM slot WHERE email_id=\"{}\"".format(request_body.email_id))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    if len(result) == 0:
        return {"status": "No slot booked yet"}
    elif len(result) == 1:
        slot_number = result[0]['slot_number']
        days_code = result[0]['days_code']
        start_date = result[0]['start_date']
        return {"status": "Fetched booked slot details successfully!",
                "slot_number": slot_number,
                "days_code": days_code,
                "start_date": start_date
                }
