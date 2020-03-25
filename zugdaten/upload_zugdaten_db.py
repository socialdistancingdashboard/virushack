""" Importiert die Backups aus dem Speicher und 
uploaded tageweise in amazon s3 """

import os
import re
import pandas as pd
from datetime import datetime
# compatibility with ipython
try:  
  __IPYTHON__
  os.chdir(os.path.dirname(__file__))
except: pass
from db import DatabaseWrapper
import json
import boto3
from pathlib import Path
import geopandas.tools
from shapely.geometry import Point
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

config = json.load(open("../credentials/credentials-aws-db.json", "r"))
aws_engine = create_engine(
  ("mysql+pymysql://" +
  config["user"] + ":" +
  config["password"] + "@" +
  config["host"] + ":" + 
  str(config["port"]) + "/" +
  config["database"]),
  poolclass=NullPool, # dont maintain a pool of connections
  pool_recycle=3600 # handles timeouts better, I think...
)

config = json.load(open("../credentials/credentials-local-db.json", "r"))
local_engine = create_engine(
  ("mysql+pymysql://" +
  config["user"] + ":" +
  config["password"] + "@" +
  config["host"] + ":" + 
  str(config["port"]) + "/" +
  config["database"]),
  poolclass=NullPool, # dont maintain a pool of connections
  pool_recycle=3600 # handles timeouts better, I think...
)


# download shapefiles
countries = geopandas.GeoDataFrame.from_file(
  "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", 
  layer=1, 
  driver="TopoJSON")
# clean unnecessary columns
countries = countries[["id", "geometry"]]
countries.columns = ["district_id", "geometry"]

locations = pd.read_sql("select * from locations", aws_engine)

# path to data source
# path = "/home/bemootzer/Documents/SoftwareProjekte/stewardless/stewardless-crawler/dbbackup"
path = "/media/bemootzer/SICHERUNG/stewardless/data"
re_sql = re.compile(r"arrival.*.sql") # only upload data from arrivals

#_, blacklist, _ = next(os.walk(os.path.join("summaries","data")))
_, blacklist, _ = next(os.walk(path))
blacklist.append("2020-02-01") # data not complete

for file in os.listdir(path): 
  if not re_sql.match(file):
    continue
    
  # LOAD BACKUP
  #file = "arrivals-2020-03-01.sql"
  date_string = file.replace("arrivals-", "").replace(".sql", "")
  if date_string in blacklist:
    print("skip %s" % file)
    continue #skip because this file was already uploaded.

  try:
    print("current file", file)
    os.system("mysql -u hafas -e 'CREATE DATABASE IF NOT EXISTS hafasdb2'")
    os.system("mysql -u hafas -e 'DROP TABLE IF EXISTS hafasdb2.arrivals'")
    os.system("mysql -u hafas --force  hafasdb2 < %s" % os.path.join(path, file))

    # RUN QUERY ON BACKUP FOR SCHEDULED STOPS
    q = """
      SELECT 
        T1.stopId, 
        T2.longitude, 
        T2.latitude, 
        lineProduct, 
        YEAR(scheduledWhen),
        MONTH(scheduledWhen),
        DAY(scheduledWhen), 
        HOUR(scheduledWhen), COUNT(*) 
      FROM arrivals AS T1
      JOIN hafasdb.stations AS T2 ON T1.stopId = T2.id
      WHERE lineProduct IN ("bus", "suburban", "regional", "nationalExpress", "national")
      GROUP BY stopID, lineProduct, YEAR(scheduledWhen), MONTH(scheduledWhen), DAY(scheduledWhen), HOUR(scheduledWhen)
    """
    df = pd.read_sql(q, local_engine) 
    df.columns = ["stopId", "lon", "lat", "lineProduct", "year", "month", "day", "hour", "planned_stops"]
    
    def setDate(series):
      return datetime(series["year"], series["month"], series["day"], series["hour"], )
    df["date"] = df.apply(setDate, axis=1)
    df.drop(["year", "month", "day", "hour"], axis=1, inplace=True)
    df = df.dropna(subset=['lon', 'lat'])

    # RUN QUERY ON BACKUP FOR CANCELLED STOPS
    q = """
      SELECT 
        T1.stopId, 
        T2.longitude, 
        T2.latitude, 
        lineProduct, 
        YEAR(scheduledWhen),
        MONTH(scheduledWhen),
        DAY(scheduledWhen), 
        HOUR(scheduledWhen),
        COUNT(*) 
      FROM arrivals AS T1
      JOIN hafasdb.stations AS T2 ON T1.stopId = T2.id
      WHERE lineProduct IN ("bus", "suburban", "regional", "nationalExpress", "national")
      AND cancelled = 1
      GROUP BY stopID, lineProduct, YEAR(scheduledWhen), MONTH(scheduledWhen), DAY(scheduledWhen), HOUR(scheduledWhen)
    """

    df_cancelled = pd.read_sql(q, local_engine) 
    df_cancelled.columns = ["stopId", "lon", "lat", "lineProduct", "year", "month", "day", "hour", "cancelled_stops"]
    df_cancelled["date"] = df_cancelled.apply(setDate, axis=1)
    df_cancelled.drop(["year", "month", "day", "hour"], axis=1, inplace=True)
    df_cancelled = df_cancelled.dropna(subset=['lon', 'lat'])

    # DO SOPHISTICATED MERGE WITH CUSTOM INDEX
    def customIndex(series):
      return str(series["stopId"]) + series["lineProduct"] + str(series["date"])
    df["customIndex"] = df.apply(customIndex, axis=1)
    df_cancelled["customIndex"] = df_cancelled.apply(customIndex, axis=1)

    df = df.merge(
      df_cancelled[["customIndex", "cancelled_stops"]], 
      on="customIndex",
      how="left",
      suffixes=(False, False))
    
    # REPLACE NULL VALUES IN CANCELLED STOPS WITH 0
    df.cancelled_stops.fillna(0, inplace=True)

    # REMOVE CUSTOM INDEX
    df.drop("customIndex", axis=1, inplace=True)

    # WRITE A SHORT DAILY SUMMARY TO DISC
    summary_path = os.path.join(os.getcwd(), "summaries", "data", date_string)
    Path(summary_path).mkdir(parents=True, exist_ok=True)
    tmp = json.loads(df.groupby(["lineProduct"]).sum()[["planned_stops", "cancelled_stops"]].to_json())
    summary = {
      "date": date_string,
      "planned_stops": tmp["planned_stops"],
      "cancelled_stops": tmp["cancelled_stops"]
    }

    # preprocess data
    def coord_to_point(x):
      return Point(x["lon"], x["lat"])
    df["geometry"] = df[["lon", "lat"]].apply(coord_to_point, axis=1)
    df = geopandas.GeoDataFrame(df, geometry="geometry")
    df = geopandas.sjoin(df, countries, how="left", op='intersects')
    df.drop(["index_right", "geometry"], axis=1, inplace=True)
    df.dropna(inplace=True) # remove those that couldnt be matched to shapes

    df.drop(["lon", "lat"], axis=1, inplace=True) # loose station coords and replace by aggregated district centroid
    
    df = df.merge(
      locations,
      on="district_id",
      how="left",
      suffixes=(False, False)
    )

    # aggregate by region
    unique_district_ids = df["district_id"].unique()
    unique_datetimes = df["date"].unique()
    unique_lineProducts = ['all', 'nationalExpress', 'regional', 'suburban', 'national', 'bus']

    cnt = 0
    scores = [] 
    meta = []
    def append_to_scores_and_meta(df_filtered, district_id, category):
      reference_value = 0 
      score_value = df_filtered.cancelled_stops.sum() / df_filtered.planned_stops.sum() 

      meta.append({
        "district_id": district_id,
        "category": category,
        "meta": None,
        "source_id": "aggregated source",
        "description": "Aggregierte Daten aller verfügbaren Haltestellen im district.",
      })

      scores.append({
        "dt": d,
        "score_value": score_value,
        "reference_value": reference_value,
        "category": category,
        "district_id": district_id,
        "source_id": "aggregated source"
      })

    for district_id in unique_district_ids:
      cnt = cnt + 1
      if cnt % 100 == 0:
        print("%2.4f" % (cnt / len(unique_district_ids)))
      
      for d in unique_datetimes:
      #d = datetime(*[int(v) for v in date_string.split("-")])
        # add score for all means of public transportation
        category = "score_public_transportation_all"
        df_filtered = df[ (df.district_id==district_id) ]
        if len(df_filtered) == 0:
          continue
        
        append_to_scores_and_meta(
          df_filtered,
          district_id,
          category
        )

        for lineProduct in unique_lineProducts:
          category = "score_public_transportation_" + lineProduct
          df_filtered = df[
            (df.district_id==district_id) & 
            (df.lineProduct==lineProduct)
          ]
          if len(df_filtered) == 0:
            continue
          
          append_to_scores_and_meta(
            df_filtered,
            district_id,
            category
          )
          


    meta = pd.DataFrame(meta)

    # use this upload to handle duplicates
    with aws_engine.connect() as cnx:
      q = """
        INSERT INTO scores_meta (district_id, category, meta, source_id, description)
        VALUES(%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE meta = meta, description = description
      """
      cnx.execute(q, meta.values.tolist() , multi=True)
    

    scores = pd.DataFrame(scores)
    
    # retrieve meta data to for all relevant categories to assign correct foreign keys to score upload
    q = ("""
      SELECT * FROM scores_meta 
      WHERE category IN 
      ( """ +
      ",".join(["'score_public_transportation_%s'" % lp for lp in unique_lineProducts])
      + ")")

    scores_meta_foreign_keys = pd.read_sql(q, aws_engine) 

    def f(x):
      return x["district_id"] + x["category"] + x["source_id"]
    scores_meta_foreign_keys["custom_index"] = scores_meta_foreign_keys.apply(f, axis=1)
    scores_meta_foreign_keys = scores_meta_foreign_keys[["custom_index", "id"]]
    scores_meta_foreign_keys.columns = ["custom_index", "meta_id"]
    scores["custom_index"] = scores.apply(f, axis=1)

    scores = scores.merge(
      scores_meta_foreign_keys,
      on="custom_index",
      how="left",
      suffixes=(False, False)
    )

    scores = scores.drop(["custom_index", "source_id"], axis=1)
    
    scores.to_sql(
      con=aws_engine,
      name="scores",
      index=False,
      #schema=config["database"], # optional
      if_exists="append",
      chunksize=500, # rows at once
    )
      
  except Exception as ex:
    print(ex)
    print("%s was not processed properly" % file)
    break

aws_engine.dispose()
local_engine.dispose()
# more information about how to close mysql connections
# https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql