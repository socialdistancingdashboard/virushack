import os
import re
import pandas as pd
from datetime import datetime, timedelta, date
# compatibility with ipython
#os.chdir(os.path.dirname(__file__))
import json
import boto3
from pathlib import Path
from coords_to_kreis import coords_convert
import settings

def aggregate(date):
    client_s3 = boto3.client("s3")
    s3 = boto3.resource('s3')
    content_object = s3.Object(settings.BUCKET, "aggdata/live/{}/{}/{}/zugdata.json".format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    df = pd.DataFrame(json_content)
    df["landkreis"] = coords_convert(df)
    print(df.shape)
    print(df["landkreis"].unique().shape)
    #df["district"] = coords_convert(df)
    #print(df.columns)
    df.drop(["lon", "lat", 'geometry', "name", "date"], inplace = True, axis = 1)
    df = df.set_index("landkreis")
    df = 1 - df
    df = df.reset_index()
    # aggregate by region		     # aggregate by region
    return df.to_dict()
#pd.DataFrame(aggregate(date.today() - timedelta(days = 4)))
