""" This script aggregates zugdata on a daily basis and uploads it in /live/aggdata """
import os
import re
import pandas as pd
from datetime import datetime
# compatibility with ipython
os.chdir(os.path.dirname(__file__))
import json
import boto3
from pathlib import Path
import geopandas.tools
from shapely.geometry import Point

# download shapefiles
countries = geopandas.GeoDataFrame.from_file(
  "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", 
  layer=1, 
  driver="TopoJSON")

# clean unnecessary columns
countries = countries[["name", "geometry"]]

# connect to aws
client_s3 = boto3.client("s3")
s3 = boto3.resource('s3')

_, folders, _ = next(os.walk(os.path.join(os.getcwd(), "..", "zugdaten", "summaries", "data")))
for date_string in folders:
  date = datetime.fromisoformat(date_string)
  print("processing", date_string)
  
  if date <= datetime(2020,3,21) or date_string == "2020-03-24":
    print("skip", date_string)
    continue
  # use this date
  #date_string = "2020-03-21"

  # get unprocessed data
  content_object = s3.Object("sdd-s3-basebucket", "zugdaten/" + date_string.replace("-","/") + "/zugdaten.json")
  file_content = content_object.get()['Body'].read().decode('utf-8')
  json_content = json.loads(file_content)

  # preprocess data
  def coord_to_point(x):
    return Point(x["lon"], x["lat"])
  df = pd.DataFrame(json_content)
  df["geometry"] = df[["lon", "lat"]].apply(coord_to_point, axis=1)
  df = geopandas.GeoDataFrame(df, geometry="geometry")
  df = geopandas.sjoin(df, countries, how="left", op='intersects')
  df.drop(["stopId", "index_right", "geometry"], axis=1, inplace=True)
  df.dropna(inplace=True) # remove those that couldnt be matched to shapes

  # aggregate by region
  regions = df["name"].unique()
  # pass several scores in one file
  lineProducts = ['nationalExpress', 'regional', 'suburban', 'national', 'bus']
  result = [] 
  for r in regions:
    # aggregate by each region
    df_filtered_by_region = df[df.name==r]

    # calculate scores
    scores = {"zug_score": df_filtered_by_region.cancelled_stops.mean() / df_filtered_by_region.planned_stops.mean()}
    for product in lineProducts:
      df_filtered_by_region_and_product = df_filtered_by_region[df_filtered_by_region.lineProduct==product]
      scores.update({product + "_score": (
        df_filtered_by_region_and_product.cancelled_stops.mean() / df_filtered_by_region_and_product.planned_stops.mean())})

    scores.update({
      "lon": df_filtered_by_region.lon.iloc[0],
      "lat": df_filtered_by_region.lat.iloc[0],
      "date": date_string,
      "name": df_filtered_by_region.name.iloc[0]
    })
    result.append(scores)
  result


  client_s3.put_object(
    Bucket="sdd-s3-basebucket", 
    Key="aggdata/live/" + date_string.replace("-", "/") + "/zugdata.json", 
    Body=json.dumps(result))