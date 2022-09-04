from fastapi import FastAPI
from mangum import Mangum
from dotenv import load_dotenv
from app.api.api_v1.api import router as api_router
import os
import mysql.connector

load_dotenv()


mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

mycursor = mydb.cursor()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": os.getenv("secretkey")}

@app.get("/fetch-all-slots")
def root():
    mycursor.execute(
        "SELECT * FROM slot")
    columns = mycursor.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in mycursor.fetchall()]
    return result



app.include_router(api_router, prefix="/api")
handler = Mangum(app)
