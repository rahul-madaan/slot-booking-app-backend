from fastapi import APIRouter
import os
import mysql.connector
from dotenv import load_dotenv
from pydantic import BaseModel
from app import cypher

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
    encrypted_email_ID_len: int


# localhost:8000/api/v1 = default
@router.post("/login")
async def login(request_body: LoginUser):
    mycursor.execute("SELECT * FROM user")
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    for credentials in result:
        if request_body.email_ID == credentials['email_ID']:
            if request_body.password == credentials['password']:
                encryptedEmail = cypher.encrypt(request_body.email_ID)
                return {'statusCode': 0, 'message': 'Login Successful', 'encrypted_emailID': encryptedEmail}
            else:
                return {'statusCode': 1, 'message': 'Password does not match'}
    else:
        return {'statusCode': 2, 'message': 'User not registered'}


@router.post("/verify-login")
async def login(request_body: VerifyLogin):
    if 5 * request_body.encrypted_email_ID_len == len(request_body.encrypted_email_ID):
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
