""" This scripts uploads location database to sdd-db """

import os
import re
import pandas as pd
from datetime import datetime
# compatibility with ipython
try:  
  __IPYTHON__
  os.chdir(os.path.dirname(__file__))
except: pass
import json
import boto3
from pathlib import Path
from shapely.geometry import Point
import pymysql 
from sqlalchemy import create_engine

config = json.load(open("../../credentials/credentials-aws-db.json", "r"))

engine = create_engine(
  ("mysql+pymysql://" +
  config["user"] + ":" +
  config["password"] + "@" +
  config["host"] + ":" + 
  str(config["port"]) + "/" +
  config["database"]),
  pool_recycle=3600 # handles timeouts better, I think...
)
  
aws_connection = engine.raw_connection()

# download shapefiles
locations = pd.read_pickle("locations.pickle")
locations = locations[["id", "name", "districtType", "state", "geometry"]]
locations.columns = ["district_id", "district", "district_type", "state", "geometry"]

locations["lat"] = locations.geometry.apply(lambda x: x.centroid.y)
locations["lon"] = locations.geometry.apply(lambda x: x.centroid.x)

df_state_ids = pd.DataFrame([
  ["Brandenburg", "BB"],
  ["Berlin", "B"],
  ["Baden-Württemberg", "BW"],
  ["Bayern", "BY"],
  ["Bremen", "HB"],
  ["Hessen", "HE"],
  ["Hamburg", "HH"],
  ["Mecklenburg-Vorpommern", "MV"],
  ["Niedersachsen", "NI"],
  ["Nordrhein-Westfalen", "NRW"],
  ["Rheinland-Pfalz", "RP"],
  ["Schleswig-Holstein", "SH"],
  ["Saarland", "SL"],
  ["Sachsen", "SN"],
  ["Sachsen-Anhalt", "SA"],
  ["Thüringen", "TH"]
], columns=["state", "state_id"])

locations["country_id"] = "DE"
locations["country"] = "Deutschland"

locations = locations.merge(
  df_state_ids,
  on="state",
  how="left",
  suffixes=(False, False))

locations["geometry"] = locations.geometry.astype(str)

query = """
  INSERT INTO locations
  (
    district_id, 
    district, 
    district_type, 
    state, 
    geometry,
    lat,
    lon,
    country_id, 
    country,
    state_id
  )
  VALUES (%s, %s, %s, %s, polygonfromtext(%s), %s, %s, %s, %s, %s)
"""

with engine.connect() as cnx:
  cnx.execute(query, locations.values.tolist() , multi=True)

