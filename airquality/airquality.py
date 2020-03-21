import base64
import datetime
import os

import boto3
import requests

import csv

cities = [
    'berlin'
]

airquality_token = os.environ['AIR_QUALITY_API_TOKEN']

client = boto3.client('firehose')

with open('kreise_mit_center.csv', newline='',encoding='utf-8') as csvfile:
    #for city in cities:
    fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
    header = next(fileReader)
    # Check file as empty
    if header != None:
        # Iterate over each row after the header in the csv
        for row in fileReader:
            print(row)
            lon = row[1]
            lat = row[2]
            url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={airquality_token}'
            response = requests.get(url)
            print(response.content)
            if response.status_code == 200:
                new_record = {
                    'landkreis_name': row[0],
                    # todo time from request
                    'datetime': datetime.datetime.now(),
                    'lat': lat,
                    'lon': lon,
                    'airquality': response.content
                }
                print(new_record)
                new_record_encoded = str(new_record).encode('utf-8')
                response = client.put_record(DeliveryStreamName='sdd-kinesis-airquality', Record={'Data': base64.b64encode(new_record_encoded)})