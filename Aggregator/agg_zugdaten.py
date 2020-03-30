""" This script aggregates zugdata on a daily basis and uploads it in /live/aggdata """
import os
import re
import pandas as pd
from datetime import datetime, timedelta
# compatibility with ipython
#os.chdir(os.path.dirname(__file__))
import json
import boto3
from pathlib import Path
from coords_to_kreis import coords_convert

def aggregate(date):
  try:
    # connect to aws
    client_s3 = boto3.client("s3")
    s3 = boto3.resource('s3')
    content_object = s3.Object("sdd-s3-basebucket", "zugdaten/{}/{}/{}/zugdaten.json".format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    df = pd.DataFrame(json_content)
    df["district"] = coords_convert(df)
    # aggregate by region
    regions = df["district"].unique()
    # pass several scores in one file
    lineProducts = ['nationalExpress', 'regional']
    result = []
    for r in regions:
      # add entry for district
      scores = {"landkreis": r}
      for product in lineProducts:
        df_filtered = df[ (df.district == r) & (df.lineProduct==product) ]
        # add scores to dictionary
        scores.update({"score_public_transportation_" + product: df_filtered.cancelled_stops.sum()})
      # add to result
      result.append(scores)
    # return result as list
    return result
  except Exception as e:
    print("Datum evt nicht vorhanden? Fehler:", str(e))
    return []
