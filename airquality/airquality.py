import base64
import datetime
import os

import boto3
import requests

cities = [
    'berlin'
]

airquality_token = os.environ['AIR_QUALITY_API_TOKEN']

client = boto3.client('firehose')

for city in cities:
    url = f'https://api.waqi.info/feed/{city}/?token={airquality_token}'
    response = requests.get(url)
    if response.status_code == 200:
        new_record = {
            'landkreis_name': city,
            'datetime': datetime.datetime.now(),
            'lat': 123,
            'lon': 123,
            'airquality': response.content
        }
        print(new_record)
        new_record_encoded = str(new_record).encode('utf-8')
        response = client.put_record(DeliveryStreamName='sdd-kinesis-airquality', Record={'Data': base64.b64encode(new_record_encoded)})