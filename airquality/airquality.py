import datetime
import os
import boto3
import requests
import csv
import json
from datetime import datetime

def to_airquality(city_name, lat, lon, response):
    data = response['data']

    return {
        'landkreis_name': city_name,
        # todo time from request
        'datetime': datetime.now().isoformat(),
        'lat': lat,
        'lon': lon,
        'airquality': {
            'aqi': data['aqi'],
            'iaqi': data['iaqi']
        }
    }


airquality_token = os.environ['AIR_QUALITY_API_TOKEN']
bucket = []

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
                bucket.append(airquality_record)

s3_client = boto3.client('s3')
date = datetime.now()

if len(bucket) > 0:
    response = s3_client.put_object(Body=json.dumps(bucket), Bucket='sdd-s3-basebucket',
                                    Key='airquality/{}/{}/{}/{}'.format(str(date.year).zfill(4),
                                                                        str(date.month).zfill(2),
                                                                        str(date.day).zfill(2),
                                                                        str(date.hour).zfill(2)))
    print("Response: " + str(response))
