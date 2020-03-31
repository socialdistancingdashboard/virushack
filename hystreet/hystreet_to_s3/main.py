import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import boto3

client = boto3.client('s3')

df = pd.DataFrame(columns=['timestamp', 'station_id', 'pedestrians_count',
                           'unverified', 'weather_condition', 'temperature', 'min_temperature'])

headers = {'Content-Type': 'application/json',
           'X-API-Token': "dWfpGRD3aBNocEbZNdLrhRDe"}
res = requests.get('https://hystreet.com/api/locations/', headers=headers)
locations = res.json()

# Crawl data
for location in locations:
    current_date = datetime.now()
    form_date = (current_date - timedelta(days=10)).strftime("%Y-%m-%d")
    to_date = current_date.strftime("%Y-%m-%d")
    res = requests.get('https://hystreet.com/api/locations/' +
                       str(location['id'])+'?resolution=day&from='+form_date+'&to='+to_date, headers=headers)
    measurements = res.json()['measurements']
    for measurement in measurements:
        measurement['station_id'] = location['id']

        date_str = measurement['timestamp'].split('+')[0]
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')

        measurement['date'] = date.strftime("%Y-%m-%d")
        df = df.append(measurement, ignore_index=True)

# Upload data to S3
for name, group in df.groupby('timestamp'):
    date_str = name.split('+')[0]
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
    print(date.strftime("%Y-%m-%d"))
    client.put_object(Body=group.to_json(orient='records'), Bucket='sdd-s3-basebucket',
                      Key='hystreet/'+str(date.year).zfill(4)+'/'+str(date.month).zfill(2)+'/'+str(date.day).zfill(2))
