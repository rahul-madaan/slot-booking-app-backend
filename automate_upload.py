import os
import boto3

os.chdir("/Users/rahul.madan/PycharmProjects/slot-booking-app-backend/venv/lib/python3.8/site-packages")
os.system("zip -r9 ../../../../function.zip .")
os.chdir("/Users/rahul.madan/PycharmProjects/slot-booking-app-backend")
os.system("zip -g ./function.zip -r app")
os.system("zip -g ./function.zip -r .env")

print("UPLOADING TO BUCKET...")
s3 = boto3.resource(service_name='s3')
BUCKET = "fastapi-slot-booking"
s3.Bucket(BUCKET).upload_file("/Users/rahul.madan/PycharmProjects/slot-booking-app-backend/function.zip", "function.zip")
os.remove('function.zip')

print("URL: https://fastapi-slot-booking.s3.ap-south-1.amazonaws.com/function.zip")
print("LAMBDA: https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/serverless-fastapi-lambda?tab=code")