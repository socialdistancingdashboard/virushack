import json


def lambda_handler(event, context):
    landkreise_ids = event['multiValueQueryStringParameters']['landkreis_ids']
    airquality_dummy_data = {
        'aqi': 2,
        'iaqi': {
            'dew': {
                'v': 3
            },
            'h': {
                'v': 95.3
            },
            'no2': {
                'v': 9.6
            },
            'o3': {
                'v': 17.9
            },
            'p': {
                'v': 1022.5
            },
            'pm10': {
                'v': 2
            },
            't': {
                'v': 3.6
            },
            'w': {
                'v': 8.2
            },
            'wg': {
                'v': 11.3
            }
        }
    }
    hystreet_dummy_data = {
        'relative_popularity': 0.1320754717
    }

    landkreise = []
    for lankreis_id in landkreise_ids:
        landkreise.append({
            'landkreis_id': lankreis_id,
            'landkreis_name': 'S\xc3\xbcdwestpfalz',
            'lat': '49.20807801390453',
            'lon': '7.65775790003346',
            'data': {
                'airquality': airquality_dummy_data,
                'hystreet': hystreet_dummy_data,
            }
        })

    response_data = json.dumps({
        'date': event['queryStringParameters']['date'],
        'landkreise': landkreise
    })

    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }


import json
import boto3
import datetime
import pandas as pd

def lambda_handler(event, context):
    print(event)


    # event["date_min"], event["date_max"]
    # min_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    # max_date = datetime.datetime.now().date()

    # pd.date_range(min_date, max_date)
    # datetime.timedelta(days=1)


    s3 = boto3.resource('s3')
    #    obj = s3.Object('sdd-s3-basebucket', 'AggregatedData/2020/03/22/sdd-kinese-aggregator-2-2020-03-22-15-28-20-0bb7c782-48b8-4478-8f95-989db4f51834')
    for date in pd.date_range(event["date_min"], event["date_max"]):
        obj = s3.Object('sdd-s3-basebucket',
                        'aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2),
                                                                  str(date.day).zfill(2)))

    return {
        'statusCode': 200,
        'body': obj.get()['Body'].read()
    }
