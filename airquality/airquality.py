import base64
import datetime
import os

import boto3
import requests

import csv
import json

airquality_token = os.environ['AIR_QUALITY_API_TOKEN']

client = boto3.client('firehose')


def to_byte_record(airquality_record):
    # new_record_encoded = str(airquality_record).encode('utf-8')

    return json.dumps(airquality_record)


def to_airquality(city_name, lat, lon, response):
    data = response['data']

    return {
        'landkreis_name': city_name,
        # todo time from request
        'datetime': datetime.datetime.now(),
        'lat': lat,
        'lon': lon,
        'airquality': {
            'aqi': data['aqi'],
            'iaqi': data['iaqi']
        }
    }


with open('kreise_mit_center.csv', newline='', encoding='utf-8') as csvfile:
    fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
    header = next(fileReader)
    # Check file as empty
    if header is not None:
        # Iterate over each row after the header in the csv
        for row in fileReader:
            city_name = row[0]
            lon = row[1]
            lat = row[2]
            url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={airquality_token}'
            response = requests.get(url)
            if response.status_code == 200 and response.json()['status'] == 'ok':
                airquality_record = to_airquality(city_name, lat, lon, response.json())
                # print(str(airquality_record).encode('utf-8'))
                client.put_record(DeliveryStreamName='sdd-kinesis-airquality',
                                  Record={'Data': to_byte_record(airquality_record)})
