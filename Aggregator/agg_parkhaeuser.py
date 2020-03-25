# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 16:47:26 2020

@author: Peter
"""

from datetime import datetime
import boto3
import json
import csv

def aggregate(date):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='parkhaeuser/{}/{}/{}/{}'.format(
        str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date.hour).zfill(2)))
    json.loads(response["Body"].read())
    results = []
    with open('zuordnung_plz_ort_landkreis.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for city in results:
            city_name = result['landkreis']
            for row in reader:
                if row['ort'].startswith(city_name):
                    ags = row['ags']
                    break
            data = {'landkreis': ags,
                'parkhaeuser_score': result['Auslastung']
                }
            results.append(data)
    return results

