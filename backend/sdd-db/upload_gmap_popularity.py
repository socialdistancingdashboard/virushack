
""" This script uploads into database from s3 bucket source 

  CAREFULL: Dont run this script twice on the same day! This will create
  duplicates that will hunt us f.o.r.e.v.e.r!

  For this reason never run this script for the current day (because you
   would need to run it twice...)
"""

from webbrowser import get
from coords_to_kreis import coords_convert
import boto3
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import csv
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import dateutil.parser

# ask parzi for credentials
config = json.load(open("../../credentials/credentials-aws-db.json", "r"))

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

q = """ SELECT * from locations """
locations = pd.read_sql(q, aws_engine)

def upload_date(date):
  """ Uploads data for given date """
  category = "score_google_places"
  s3_client = boto3.client('s3')

  print("processing", date)

  # for some reason data is only crawled from 9am to 7pm. This script supports changes to this habit by trial and error requests
  hours = range(0,24)
  metas = []
  scores = []

  def add_items(hour, score, station):
    coordinates = pd.DataFrame([station["coordinates"]])
    coordinates.rename(columns={"lng": "lon"}, inplace=True)
    district_id = coords_convert(coordinates).values[0]

    meta = {
      "station_id": station["id"],
      "station_name": station["name"],
      "address": station["address"],
      "station_types": station["types"],
      "station_lon": station["coordinates"]["lng"],
      "station_lat": station["coordinates"]["lat"],
      "station_rating": station["rating"],
      "station_rating_n": station["rating_n"]
    }

    metas.append({
    "district_id": district_id,
    "category": category,
    "meta": json.dumps(meta),
    "description": station["name"],
    "source_id": station["id"]
    })

    scores.append({
      "dt": datetime(date.year, date.month, date.day, hour),
      "score_value": score,
      "reference_value": 0,
      "category": category,
      "district_id": district_id,
      "source_id": station["id"],
    })

  available_hours = set()
  for hour in hours:
    try:
      response = s3_client.get_object(
        Bucket='sdd-s3-basebucket', 
        Key='googleplaces/{}/{}/{}/{}'.format(
          str(date.year).zfill(4),
          str(date.month).zfill(2),
          str(date.day).zfill(2),
          str(hour).zfill(2)))
      
      # used to approximate date that was not hourly crawled
      available_hours = available_hours.union({hour})

      result = json.loads(response["Body"].read())
    except:
      continue

    for station in result:
      score = station["current_popularity"]
      add_items(hour, score, station)
  

  unavailable_hours = set(hours) - available_hours
  
  # approximate values for night times by using the last available 24h data from 6pm
  hour = max(available_hours)
  # approximate score by using the score from the last available our of the day
  response = s3_client.get_object(
    Bucket='sdd-s3-basebucket', 
    Key='googleplaces/{}/{}/{}/{}'.format(
      str(date.year).zfill(4),
      str(date.month).zfill(2),
      str(date.day).zfill(2),
      str(hour).zfill(2)))
  result = json.loads(response["Body"].read())
  
  for hour_night in unavailable_hours:
    for station in result:
      score = station["populartimes"][0]["data"][hour_night]  
    
    for station in result:
      add_items(hour, score, station)
    
   
  # upload metas
  if len(metas) > 0:
    q = """
      REPLACE INTO scores_meta 
      (
        district_id,
        category,
        meta,
        description,
        source_id
      )
      VALUES (%s, %s, %s, %s, %s )
    """
    df_meta = pd.DataFrame(metas).drop_duplicates()
    with aws_engine.connect() as cnx:
      cnx.execute(q, df_meta.values.tolist() , multi=True)

  # upload scores
  if len(scores) > 0:
    q = """
      SELECT id AS meta_id, source_id FROM scores_meta 
      WHERE category = '%s' 
    """ % category
    
    scores_meta_foreign_keys = pd.read_sql(q, aws_engine) 
    scores = pd.DataFrame(scores)
    scores = scores.merge(
      scores_meta_foreign_keys,
      on="source_id",
      how="left",
      suffixes=(False, False)
    )

    scores.to_sql(
      con=aws_engine,
      name="scores",
      index=False,
      #schema=config["database"], # optional
      if_exists="append",
      chunksize=500, # rows at once
    )

    print("upload completed")

def upload_all():
  first_date_available = datetime(2020, 3, 22) # used in get-all-data mode  
  now = datetime.now()
  d = first_date_available

  # DONT upload current day. this will fuck up everything. 
  while d < datetime(now.year, now.month, now.day):
    upload_date(d)
    d = d + timedelta(days=1)
    

upload_all()
