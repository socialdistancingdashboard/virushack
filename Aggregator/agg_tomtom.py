import json
import boto3
from coords_to_kreis import coords_convert
import datetime
import pandas as pd
import numpy as np
import settings

def aggregate(date):
    s3_client = boto3.client('s3')
    #date = datetime.date.today() - datetime.timedelta(days=1)
    response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='tomtom/{}/{}/{}.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date)))
    data_current = pd.DataFrame(json.loads(response["Body"].read()))
    data_current["ags"] = coords_convert(data_current)
    data_current["score"] = data_current["TrafficIndexLive"] / data_current["TrafficIndexHistoric"]
    data_current.replace(np.inf, np.nan, inplace=True)
    result = pd.DataFrame(data_current.groupby("ags")["score"].mean())

    result = result.reset_index()
    list_results = []

    for index, row in result.iterrows():
        landkreis = row['ags']
        relative_popularity = row["score"]
        data_index = {
            "landkreis": landkreis,
            'tomtom_score' : relative_popularity
        }
        list_results.append(data_index)
    return list_results
#
#aggregate(datetime.date.today() - datetime.timedelta(days = 3))
