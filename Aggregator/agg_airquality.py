import json
from datetime import date
import boto3
import pandas as pd
from pandas.io.json import json_normalize

#date = date.today()


def aggregate(date):
    s3_client = boto3.client('s3')

    merged = pd.DataFrame()
    object_list = []
    s3_objects = s3_client.list_objects_v2(Bucket='sdd-s3-basebucket',
                                           Prefix='airquality/{}/{}/{}/'.format(str(date.year).zfill(4),
                                                                                str(date.month).zfill(2),
                                                                                str(date.day).zfill(2)))
    if 'Contents' not in s3_objects:
        return []

    print("Found " + str(len(s3_objects['Contents'])) + " elements")
    for key in s3_objects['Contents']:
        airqualityObject = s3_client.get_object(Bucket='sdd-s3-basebucket', Key=key['Key'])
        object_body = str(airqualityObject["Body"].read(), 'utf-8')
        airquality_json = json_normalize(json.loads(object_body))

        object_list.append(pd.DataFrame(airquality_json))

    merged = pd.concat(object_list)

    merged['airquality.aqi'] = pd.to_numeric(merged['airquality.aqi'], errors='coerce')
    merged = merged.groupby("landkreis_name")["airquality.aqi"].mean() / 100

    merged = merged.reset_index()
    list_results = []
    for index, row in merged.iterrows():
        landkreis = row['landkreis_name']
        airquality = row['airquality.aqi']
        data_index = {
            'landkreis': landkreis,
            'airquality_score': airquality
        }
        list_results.append(data_index)
    return list_results
