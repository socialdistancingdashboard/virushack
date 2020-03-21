import boto3
import json
import populartimes
from datetime import datetime
import time
import os

if "googleapis_keys" in os.environ:
    api_key = os.environ["googleapis_keys"]
else:
    with open("google_places_popularity/api_keys.txt") as f:
        api_key = f.readline()

date = datetime.now()
with open("google_places_popularity/place_ids/staedte_koordinaten_ueber_50k_ids.csv") as f:
        place_ids = [id.strip() for id in f.readlines()]

result = []
for x, place_id in enumerate(place_ids[:4]):
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

client = boto3.client('s3')
client.put_object(Body=json.dumps(result),  Bucket='sdd-s3-basebucket',
              Key='googleplaces/{}/{}/{}/{}.json'.format(str(date.year), str(date.month).zfill(2), str(date.day), str(date.hour)))
