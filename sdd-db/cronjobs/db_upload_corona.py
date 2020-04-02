""" Uploads Corona data from Zeit online
Note: infected numbers are known infections on a particular day.
Dead and Recovered numbers were summed up until today. """

import os
import pandas as pd
from datetime import datetime, timedelta
# compatibility with ipython
try:  
  __IPYTHON__
  os.chdir(os.path.dirname(__file__))
except: pass
import json
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import urllib.request

# connect to aws database
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

# retrieve data from zeit interactive
url_corona = "https://interactive.zeit.de/cronjobs/2020/corona/germany.json"
import requests
r = requests.get(url_corona)
data = r.json()

# name the new sources
source_id_corona_dead = "corona_dead"
source_id_corona_recovered = "corona_recovered"
source_id_corona_infected = "corona_infected"

# the beginning of the data
history_start = datetime.fromisoformat(data["kreise"]["meta"]["historicalStats"]["start"])
# the last day of the data
history_end = datetime.fromisoformat(data["kreise"]["meta"]["historicalStats"]["end"])


scores = [] # rows to add in table scores
stations = [] # rows to add in table stations
# add infected by iterating over history from zeit data
for district in data["kreise"]["items"]:
  district_id = district["ags"]
  history = district["historicalStats"]["count"]
  # copy start date
  current_date = datetime.fromtimestamp(history_start.timestamp())
  stations.append({
    "district_id": district_id,
    "source_id": source_id_corona_infected
  })
  for i, number_infected in enumerate(history):
    print(current_date)
    scores.append({
      "dt": current_date,
      "score_value": number_infected,
      "source_id": source_id_corona_infected,
      "district_id": district_id,
    })
    current_date = current_date + timedelta(days=1)


## upload stations (ignore duplicates)
q = """
  INSERT IGNORE INTO stations 
    ( district_id, source_id )
  VALUES (%s, %s )
  """

df_stations = pd.DataFrame(stations)
# perform the upload task
with aws_engine.connect() as cnx:
  cnx.execute(q, df_stations.values.tolist() , multi=True)

## upload scores
# first retrieve the foreign keys
q = """
  SELECT id AS station_id, district_id FROM stations 
  WHERE source_id = '%s' 
""" % source_id_corona_infected
    
stations_foreign_keys = pd.read_sql(q, aws_engine) 
    
df_scores = pd.DataFrame(scores)

df_scores = df_scores.merge(
  stations_foreign_keys,
  on="district_id",
  how="left",
  suffixes=(False, False)
)

# some districts lack data from yesterday. skip them for now and try again tomorrow
df_scores.dropna(how='any', inplace=True) 

# dont upload dt as such because this is treated as timestamp. We want to have a german date without timezone information
df_scores['dt'] = df_scores['dt'].astype(str)
q = """
  INSERT IGNORE INTO scores 
  (
    dt,
    score_value,
    source_id,
    district_id,
    station_id
  )
  VALUES (%s, %s, %s, %s, %s)
"""
#df_scores = df_scores.drop_duplicates()
with aws_engine.connect() as cnx:
  # makes sure the columns' order match the query
  cnx.execute(q, df_scores[["dt", "score_value", "source_id", "district_id", "station_id"]].values.tolist() , multi=True)


## upload data for recovered and dead corona patients
for category in ["recovered", "dead"]:
  scores = [] # rows to add in table scores
  stations = [] # rows to add in table stations
  # add infected by iterating over history from zeit data
  for district in data["kreise"]["items"]:
    district_id = district["ags"]
    score = district["currentStats"][category]

    stations.append({
      "district_id": district_id,
      "source_id": source_id_corona_recovered
    })
    scores.append({
      "dt": history_end,
      "score_value": score,
      "source_id": "corona_" + category,
      "district_id": district_id,
    })

  ## upload stations (ignore duplicates)
  q = """
    INSERT IGNORE INTO stations 
      ( district_id, source_id )
    VALUES (%s, %s )
    """

  df_stations = pd.DataFrame(stations)
  # perform the upload task
  with aws_engine.connect() as cnx:
    cnx.execute(q, df_stations.values.tolist() , multi=True)

  ## upload scores
  # first retrieve the foreign keys
  q = """
    SELECT id AS station_id, district_id FROM stations 
    WHERE source_id = '%s' 
  """ % source_id_corona_infected
      
  stations_foreign_keys = pd.read_sql(q, aws_engine) 
    
  df_scores = pd.DataFrame(scores)

  df_scores = df_scores.merge(
    stations_foreign_keys,
    on="district_id",
    how="left",
    suffixes=(False, False)
  )

  # some districts lack data from yesterday. skip them for now and try again tomorrow
  df_scores.dropna(how='any', inplace=True) 

  # dont upload dt as such because this is treated as timestamp. We want to have a german date without timezone information
  df_scores['dt'] = df_scores['dt'].astype(str)
  q = """
    INSERT IGNORE INTO scores 
    (
      dt,
      score_value,
      source_id,
      district_id,
      station_id
    )
    VALUES (%s, %s, %s, %s, %s)
  """
  #df_scores = df_scores.drop_duplicates()
  with aws_engine.connect() as cnx:
    # makes sure the columns' order match the query
    cnx.execute(q, df_scores[["dt", "score_value", "source_id", "district_id", "station_id"]].values.tolist() , multi=True)
