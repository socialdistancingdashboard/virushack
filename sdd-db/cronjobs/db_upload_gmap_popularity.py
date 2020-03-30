
""" This script uploads into database from s3 bucket source
This should be run daily on any machine that meets the python dependencies.
"""

try:  # allows to import local modules
  __IPYTHON__ 
  os.chdir(os.path.dirname(__file__))
except: pass
from coords_to_kreis import coords_convert
import boto3
import json
from datetime import datetime, timedelta
import pandas as pd
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

source_id = "score_google_places"
s3_client = boto3.client('s3')

q = """ SELECT * from locations """
locations = pd.read_sql(q, aws_engine)

def custom_index(x):
  """ used to merge foreign station keys on scores """
  return str(x["district_id"]) + str(x["description"]) + str(x["source_station_id"])


def upload_date(date):
  """ Uploads data for given date """
  print("processing", date)

  stations = []
  scores = []
  for hour in range(0,24):
    try:
      response = s3_client.get_object(
        Bucket='sdd-s3-basebucket', 
        Key='googleplaces/{}/{}/{}/{}'.format(
          str(date.year).zfill(4),
          str(date.month).zfill(2),
          str(date.day).zfill(2),
          str(hour).zfill(2)))
      
      result = json.loads(response["Body"].read())
    except:
      continue

    for station in result:
      
      score_value = station["current_popularity"]
      try:
        score_reference = station["populartimes"][date.weekday()]["data"][hour]
      except:
        score_reference = None

      coordinates = pd.DataFrame([station["coordinates"]])
      coordinates.rename(columns={"lng": "lon"}, inplace=True)
      district_id = coords_convert(coordinates).values[0]

      other = {
        "googleplaces_id": station["id"],
        "station_name": station["name"],
        "address": station["address"],
        "station_types": station["types"],
        "station_lon": station["coordinates"]["lng"],
        "station_lat": station["coordinates"]["lat"],
        "station_rating": station["rating"],
        "station_rating_n": station["rating_n"]
      }

      stations.append({
        "district_id": district_id,
        "source_id": source_id,
        "other": json.dumps(other),
        "description": station["name"],
        "source_station_id": station["id"],
      })

      other = {
        # dont loose this information
        "populartimes": station["populartimes"]
      }

      scores.append({
        "dt": datetime(date.year, date.month, date.day, hour),
        "score_value": score_value,
        "reference_value": score_reference,
        "source_id": source_id,
        "district_id": district_id,
        "source_station_id": station["id"],
        "description": station["name"],
        "other": json.dumps(other)
      })


  # upload stations. handles duplicates so dont worry
  if len(stations) > 0:
    q = """
      INSERT IGNORE INTO stations 
      (
        district_id,
        source_id,
        other,
        description,
        source_station_id
      )
      VALUES (%s, %s, %s, %s, %s )
    """
    df_stations = pd.DataFrame(stations).drop_duplicates()
    with aws_engine.connect() as cnx:
      cnx.execute(q, df_stations.values.tolist() , multi=True)

  # upload scores
  if len(scores) > 0:
    q = """
      SELECT id AS station_id, district_id, description, source_station_id FROM stations 
      WHERE source_id = '%s' 
    """ % source_id
    
    scores_stations_foreign_keys = pd.read_sql(q, aws_engine) 
    scores_stations_foreign_keys["custom_index"] = scores_stations_foreign_keys.apply(custom_index, axis=1)
    scores_stations_foreign_keys.drop(["district_id", "description", "source_station_id"], axis=1, inplace=True)
    
    df_scores = pd.DataFrame(scores)
    df_scores["custom_index"] = df_scores.apply(custom_index, axis=1)
    
    df_scores = df_scores.merge(
      scores_stations_foreign_keys,
      on="custom_index",
      how="left",
      suffixes=(False, False)
    )
    df_scores.drop(["description", "source_station_id", "custom_index"], axis=1, inplace=True)
    df_scores['dt'] = df_scores['dt'].astype(str)
    q = """
      INSERT IGNORE INTO scores 
      (
        dt,
        score_value,
        reference_value,
        source_id,
        district_id,
        station_id,
        other
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    df_scores = df_scores.drop_duplicates()
    with aws_engine.connect() as cnx:
      # makes sure the columns' order match the query
      cnx.execute(q, df_scores[["dt", "score_value", "reference_value", "source_id", "district_id", "station_id", "other"]].values.tolist() , multi=True)

    print("upload completed")

def upload_all():
  first_date_available = datetime(2020, 3, 22) # used in get-all-data mode  
  now = datetime.now()
  d = first_date_available

  # upload until yesterday (including)
  while d < datetime(now.year, now.month, now.day):
    upload_date(d)
    d = d + timedelta(days=1)
    

upload_all()
