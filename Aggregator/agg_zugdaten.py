""" This script aggregates zugdata on a daily basis and uploads it in /live/aggdata """
import os
import re
import pandas as pd
from datetime import datetime, date, timedelta
# compatibility with ipython
#os.chdir(os.path.dirname(__file__))
import json
import boto3
from pathlib import Path
from coords_to_kreis import coords_convert

def aggregate(date):
    # connect to aws
    client_s3 = boto3.client("s3")
    s3 = boto3.resource('s3')
    content_object = s3.Object("sdd-s3-basebucket", "aggdata/live/{}/{}/{}/zugdata.json".format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    df = pd.DataFrame(json_content)
    df["landkreis"] = coords_convert(df)
    #print(df.columns)
    df.drop(["lon", "lat", 'geometry', "name", "date"], inplace = True, axis = 1)
    # aggregate by region
    return df.to_dict()
    #df.rename(columns={"name": "landkreis"})
    # pass several scores in one file
    #lineProducts = ['nationalExpress', 'regional', 'suburban', 'national', 'bus']
    # print(df)
    # result = []
    # for r in regions:
    #     df_filtered_by_region = df[df.name==r]
    #     scores = {"zug_score": 1 - df_filtered_by_region.cancelled_stops.mean() / df_filtered_by_region.planned_stops.mean()}
    #     for product in lineProducts:
    #       df_filtered_by_region_and_product = df_filtered_by_region[df_filtered_by_region.lineProduct==product]
    #       scores.update({product + "_score": (
    #         1 - df_filtered_by_region_and_product.cancelled_stops.mean() / df_filtered_by_region_and_product.planned_stops.mean())})
    #     if len(df_filtered_by_region["name"].values) < 1:
    #         break
    #     scores.update({
    #       "landkreis": df_filtered_by_region["name"].values[0]
    #     })
    #     result.append(scores)
    #     #break
    # return result

#pd.DataFrame(aggregate(date.today() - timedelta(days = 3)))
