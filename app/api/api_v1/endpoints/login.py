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


class VerifyLogin(BaseModel):
    encrypted_email_ID: str
    encrypted_email_ID_len: str


class ReserveSlot(BaseModel):
    email_ID: str
    days_code: str
    slot_number: int


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
                email_len=cypher.encrypt(str(len(request_body.email_ID)))
                return {'statusCode': 0, 'message': 'Login Successful', 'encrypted_emailID': encryptedEmail, 'email_len': email_len}
            else:
                return {'statusCode': 1, 'message': 'Password does not match'}
    else:
        return {'statusCode': 2, 'message': 'User not registered'}


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
    mycursor.execute("SELECT email_id,booking_status  FROM slot".format(request_body.days_code,request_body.slot_number))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    for slot in result:
        if slot['email_id'] == request_body.email_ID and slot['booking_status'] == "BOOKED":
            return {"Status": "1 slot already booked"}
        elif slot['email_id'] == request_body.email_ID and slot['booking_status'] == "TEMP_BOOKED":
            mycursor.execute("DELETE FROM slot where email_id = \"{}\"".format(request_body.email_ID))
            mydb.commit()
    mycursor.execute("SELECT * FROM slot WHERE days_code=\"{}\" AND slot_number = {}".format(request_body.days_code,request_body.slot_number))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    if len(result)<int(os.getenv("TOTAL_SLOTS_PER_BATCH")):
        mycursor.execute("INSERT INTO slot (email_id, slot_number, days_code, booking_status) VALUES (\"{}\",{},\"{}\",\"TEMP_BOOKED\")".format(request_body.email_ID,request_body.slot_number,request_body.days_code))
        mydb.commit()
        return {"Status": "TEMP_BOOKED"}
    else:
        return {"Status": "ALREADY_FULL"}


@router.get("/available-slots/{days_code}")
async def available_slots(days_code):
    mycursor.execute("DELETE FROM slot WHERE booking_status = \"TEMP_BOOKED\" AND booking_time < \"{}\"".format(str(datetime.now()-timedelta(minutes=15))[:19]))
    mydb.commit()
    mycursor.execute("SELECT * FROM slot WHERE days_code=\"{}\"".format(days_code))
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    available_slots = [0]*8
    total_slots = int(os.getenv("TOTAL_SLOTS_PER_BATCH"))
    for slot_detail in result:
        slot_number = slot_detail["slot_number"]
        available_slots[slot_number-1] += 1
    for i in range(len(available_slots)):
        available_slots[i] = total_slots - available_slots[i]

    return {"available_slots": available_slots}
