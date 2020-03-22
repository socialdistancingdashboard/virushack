import boto3
import json
import populartimes
from datetime import datetime
import time
import os
import pandas as pd


s3_client = boto3.client('s3')
response = s3_client.get_object(Bucket="sdd-s3-basebucket", Key="codebuild-googleplaces/places")
api_key = response["Body"].read().decode("utf-8")
date = datetime.now()

response = s3_client.get_object(Bucket="sdd-s3-basebucket", Key="codebuild-googleplaces/2153_staedte_koordinaten.csv")

city_csv = pd.read_csv(response["Body"], sep=";", header=None)

# place_ids = [id.strip() for id in city_csv.readlines()]

place_ids = city_csv[0]

result = []
for place_id in place_ids:
    print("processing", place_id)
    try:
        key = api_key
        data = populartimes.get_id(key, place_id)
    except Exception as e:
        print(e)
        print("Error with key: " + place_id)
        continue
    if "current_popularity" in data:
        result.append(data)
    else:
        print("No Popularity-Data for " + data["name"])

s3_client.put_object(Body=json.dumps(result),  Bucket='sdd-s3-basebucket',
              Key='googleplaces/{}/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date.hour).zfill(2)))
