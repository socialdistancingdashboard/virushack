import json
import boto3
from coords_to_kreis import coords_convert
import datetime
import pandas as pd

def aggregate(date):
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='fahrrad/{}/{}/{}/{}.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date)))
    data_current = pd.DataFrame(json.loads(response["Body"].read()))
    data_current["ags"] = coords_convert(data_current)
    data_current["bike_count"] = data_current["bike_count"].astype(int)
    data_current = pd.DataFrame(data_current.groupby("ags")["bike_count"].mean())

    date = date - datetime.timedelta(days = 364) #One year ago same weekday
    response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='fahrrad/{}/{}/{}/{}.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date)))
    data_normal = pd.DataFrame(json.loads(response["Body"].read()))
    data_normal["ags"] = coords_convert(data_normal)
    data_normal["bike_count"] = data_normal["bike_count"].astype(int)
    data_normal = pd.DataFrame(data_normal.groupby("ags")["bike_count"].mean())

    result = data_current.join(data_normal, rsuffix = "normal")
    result = result.reset_index()
    list_results = []

    for index, row in result.iterrows():
        landkreis = row['ags']
        relative_popularity = row["bike_count"]/row["bike_countnormal"]
        data_index = {
            "landkreis": landkreis,
            'bike_score' : relative_popularity
        }
        list_results.append(data_index)
    return list_results
