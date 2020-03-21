""" Importiert die Backups aus dem Speicher und 
uploaded tageweise in amazon s3 """

import os
import re
import pandas as pd
from datetime import datetime
# compatibility with ipython
# os.chdir(os.path.dirname(__file__))
from db import DatabaseWrapper
import json
import boto3
from pathlib import Path

db = DatabaseWrapper("localhost", "hafasdb2", "hafas", "123")

path = "/media/bemootzer/SICHERUNG/stewardless/data"
re_sql = re.compile(r"arrival.*.sql")

_, blacklist, _ = next(os.walk(os.path.join("summaries","data")))

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
      result_alle = db.execute(q)

      df = pd.DataFrame(result_alle, columns=["stopId", "lon", "lat", "lineProduct", "year", "month", "day", "hour", "planned_stops"])
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
          HOUR(scheduledWhen), COUNT(*) 
        FROM arrivals AS T1
        JOIN hafasdb.stations AS T2 ON T1.stopId = T2.id
        WHERE lineProduct IN ("bus", "suburban", "regional", "nationalExpress", "national")
        AND cancelled = 1
        GROUP BY stopID, lineProduct, YEAR(scheduledWhen), MONTH(scheduledWhen), DAY(scheduledWhen), HOUR(scheduledWhen)
      """
      result_cancelled = db.execute(q)

      df_cancelled = pd.DataFrame(result_cancelled, columns=[
        "stopId", "lon", "lat", "lineProduct", "year", "month", "day", "hour", "cancelled_stops"])
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
      with open(os.path.join(summary_path, date_string + ".json"), "w+") as f:
        json.dump(summary, f, indent=2)
      
      # UPLOAD JSON TO AMAZON
      j = json.loads(df.to_json(orient="records"))
      
      client_s3 = boto3.client("s3"
        #region_name="eu-central-1"
      )

      response = client_s3.put_object(
        Bucket="sdd-s3-basebucket",
        Body=json.dumps(j),     
        Key="zugdaten/2020/03/21/zugdaten.json"
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
