import boto3
import os
from datetime import datetime, timedelta

from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from fastapi import APIRouter

router = APIRouter()

load_dotenv()

dynamo_resource = boto3.resource(service_name=os.getenv("AWS_SERVICE_NAME"),
                                 region_name=os.getenv("AWS_REGION_NAME"))

product_table = dynamo_resource.Table('dbms-student-details')

# df = pd.read_csv("dbms students details.csv")
#
# print(df)
#
# for i in range(164):
#     product_table.put_item(
#         Item={"net_id": df.at[i,'Username'],
#               "roll_number": str(df.at[i,'Student ID']),
#               "first_name": df.at[i,"First Name"],
#               "last_name": df.at[i,'Last Name']
#               }
#     )
#
# product_table.update_item(
#     Key={
#         'email_id': "lm222@snu.edu.in"
#     },
#     UpdateExpression="SET attendance_record = list_append(attendance_record, :i)",
#     ExpressionAttributeValues={
#         ':i': [{
#             "date": str(datetime.now())[:10],
#             "attendance": "ABSENT",
#             "IP_address": "1.2.3.4",
#             "browser_fingerprint": "lolo"
#         }],
#     },
#     ReturnValues="UPDATED_NEW"
# )

result = (
    product_table.query(KeyConditionExpression=Key('net_id').eq("am795"))['Items'])
# #
# product_table.query(IndexName="browser_fingerprint-index",
#                     KeyConditionExpression=Key('browser_fingerprint').eq("lol"))['Items'])

# product_table.scan(
#                     FilterExpression=Key('attendance_record').eq("2022-10-14"))['Items'])
print(result)

## RETRIEVE FULL DATA FROM TABLE
lastEvaluatedKey = None
items = [] # Result Array
while True:
    if lastEvaluatedKey == None:
        response = product_table.scan()  # This only runs the first time - provide no ExclusiveStartKey initially
    else:
        response = product_table.scan(
            ExclusiveStartKey=lastEvaluatedKey  # In subsequent calls, provide the ExclusiveStartKey
        )
    items.extend(response['Items'])  # Appending to our resultset list

    # Set our lastEvaluatedKey to the value for next operation,
    # else, there's no more results and we can exit
    if 'LastEvaluatedKey' in response:
        lastEvaluatedKey = response['LastEvaluatedKey']
    else:
        break
print(items)
print(len(items))  # Return Value: 6
