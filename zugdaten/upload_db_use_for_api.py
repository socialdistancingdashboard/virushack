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

# download shapefiles
countries = geopandas.GeoDataFrame.from_file(
  "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", 
  layer=1, 
  driver="TopoJSON")
# clean unnecessary columns
countries = countries[["id", "name", "geometry"]]
countries.columns = ["landkreise_id", "landkreis", "geometry"]

db = DatabaseWrapper("localhost", "hafasdb2", "hafas", "123")

connection_aws = pymysql.connect(
  host=config["host"],
  user=config["user"],
  password=config["password"],                             
  db=config["database"],
  charset='utf8mb4',
  cursorclass=pymysql.cursors.DictCursor)

connection_local = pymysql.connect(
  host="localhost",
  user="hafas",
  password="123",                             
  db="hafasdb2",
  charset='utf8mb4',
  cursorclass=pymysql.cursors.DictCursor)


conf = json.load(open("sdd-db.conf", "r"))

# ask Parzival for permissions
db_aws = DatabaseWrapper(
  database=conf["database"],
  host=conf["host"],
  user=conf["user"],
  password=conf["password"]
)


path = "/home/bemootzer/Documents/SoftwareProjekte/stewardless/stewardless-crawler/dbbackup"
#path = "/media/bemootzer/SICHERUNG/stewardless/data"
re_sql = re.compile(r"arrival.*.sql")

#_, blacklist, _ = next(os.walk(os.path.join("summaries","data")))
_, blacklist, _ = next(os.walk(path))
blacklist.append("2020-02-01") # data not complete

for file in os.listdir(path): 
  if re_sql.match(file):
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
      df = pd.read_sql(q, connection_local) 
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

      df_cancelled = pd.read_sql(q, connection_local) 
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

      # aggregate by region
      unique_regions = df["landkreise_id"].unique()
      unique_datetimes = df["date"].unique()
      unique_lineProducts = ['nationalExpress', 'regional', 'suburban', 'national', 'bus']


      cnt = 0
      result = [] 
      for r in unique_regions:
        cnt = cnt + 1
        print("%2.4f" % (cnt / len(unique_regions)))
        
        for d in unique_datetimes:
          # for p in unique_lineProducts:
          #   cnt =+ 1
          #   if cnt % 100 == 0: print("%2,2f" % (cnt / (len(unique_datetimes)*len(unique_lineProducts)*len(unique_regions))))
          #   # filter accordingly
          #   df_filtered = df[(df.name==r) & (df.date == d) & (df.lineProduct == p)]
          #   score_reference = df_filtered.planned_stops.mean() 
          #   score_absolute = df_filtered.cancelled_stops.mean()
          #   score_value = score_reference / score_absolute
          #   if len(df_filtered) > 0:
          #     result.append({
          #       "region": r,
          #       "lon": df_filtered.lon.iloc[0],
          #       "lat": df_filtered.lat.iloc[0],
          #       "date": d,
          #       "absolute_value": score_absolute,
          #       "reference_value": score_reference,
          #       "score_value": score_value,
          #       "name": unique_lineProducts
          #     })
        # for all trains
            df_filtered = df[(df.name==r) & (df.date == d)]
            score_reference = df_filtered.planned_stops.sum() 
            score_absolute = df_filtered.cancelled_stops.sum()
            score_value = score_reference / score_absolute
            if len(df_filtered) > 0:
              result.append({
                "region": r,
                "lon": df_filtered.lon.iloc[0],
                "lat": df_filtered.lat.iloc[0],
                "date": d,
                "absolute_value": score_absolute,
                "reference_value": score_reference,
                "score_value": score_value,
                "name": "all",
                "cnt": len(df_filtered)
              })

      df_db = pd.DataFrame(result, columns=["region", "lon", "lat", "date", "absolute_value", "reference_value", "score_value", "name", "cnt"])


      q = """
        INSERT INTO scores (ags) VALUES (%s)
      """
      data = [("01234345", )]
      db_aws.execute_many(q, data )


      print(len(df_db))



      with open(os.path.join(summary_path, date_string + ".json"), "w+") as f:
        json.dump(summary, f, indent=2)
      
      break
    except:
      pass

      # UPLOAD JSON TO AMAZON
      j = json.loads(df.to_json(orient="records"))
      
      client_s3 = boto3.client("s3"#region_name="eu-central-1"
      )

      response = client_s3.put_object(
        Bucket="sdd-s3-basebucket",
        Body=json.dumps(j),     
        Key="zugdaten/" + "/".join(date_string.split("-")) + "/zugdaten.json"
      )

      print("upload successfull", file)

      # for small uploads
      # client = boto3.client("firehose")
      # response = client.put_record(
      #   DeliveryStreamName='zugdaten', 
      #   Record={
      #     'Data': json.dumps(j[0])
      #   })
    except Exception as ex:
      print(ex)
      print("%s was not processed properly" % file)
  else:
    print("False")
