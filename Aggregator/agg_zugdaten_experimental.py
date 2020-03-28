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

date = date.today() - timedelta(days = 4)
    # connect to aws

date.weekday()
client_s3 = boto3.client("s3")
s3 = boto3.resource('s3')
content_object = s3.Object("sdd-s3-basebucket", "zugdaten/{}/{}/{}/zugdaten.json".format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
file_content = content_object.get()['Body'].read().decode('utf-8')
json_content = json.loads(file_content)

df = pd.DataFrame(json_content)
df["resulting_stops"] = df["planned_stops"] - df["cancelled_stops"]
df["name"] = coords_convert(df)

# aggregate by region
regions = df["name"].unique()
r=regions[0]
date_normal = datetime(2020, 2, 10) + timedelta(days = date.weekday())

content_object = s3.Object("sdd-s3-basebucket", "zugdaten/{}/{}/{}/zugdaten.json".format(str(date_normal.year).zfill(4), str(date_normal.month).zfill(2), str(date_normal.day).zfill(2)))
file_content = content_object.get()['Body'].read().decode('utf-8')
json_content = json.loads(file_content)
df_normal = pd.DataFrame(json_content)
df_normal["resulting_stops"] = df_normal["planned_stops"] - df_normal["cancelled_stops"]
df_normal["name"] = coords_convert(df_normal)

df["date"]
df_normal["date"]
# pass several scores in one file
lineProducts = ['nationalExpress', 'regional', 'suburban', 'national', 'bus']
result = []
for r in regions:
    df_filtered_by_region = df[df.name==r]
    df_normal_filtered_by_region = df_normal[df_normal.name==r]
    scores = {"zug_score": df_filtered_by_region.resulting_stops.sum() / df_normal_filtered_by_region.resulting_stops.sum()}
    for product in lineProducts:
      df_filtered_by_region_and_product = df_filtered_by_region[df_filtered_by_region.lineProduct==product]
      df_normal_filtered_by_region_and_product = df_normal_filtered_by_region[df_normal_filtered_by_region.lineProduct==product]
      scores.update({product + "_score": (
        df_filtered_by_region_and_product.resulting_stops.sum() / df_normal_filtered_by_region_and_product.resulting_stops.sum())})
    if len(df_filtered_by_region["name"].values) < 1:
        break
    scores.update({
      "landkreis": df_filtered_by_region["name"].values[0]
    })
    result.append(scores)
    #break
result
df_filtered_by_region.resulting_stops.mean()
df_normal_filtered_by_region.resulting_stops.mean()

#aggregate(date.today() - timedelta(days = 3))
