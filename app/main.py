from fastapi import FastAPI
from mangum import Mangum
from dotenv import load_dotenv
from app.api.api_v1.api import router as api_router
import os
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api")
handler = Mangum(app)
