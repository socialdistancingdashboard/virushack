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
import geopandas.tools
from shapely.geometry import Point
import pymysql 
from sqlalchemy import create_engine

config = json.load(open("sdd-db.conf", "r"))

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
countries = geopandas.GeoDataFrame.from_file(
  "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", 
  layer=1, 
  driver="TopoJSON")
# clean unnecessary columns
countries = countries[["id", "name", "districtType", "state", "geometry"]]
countries.columns = ["landkreis_id", "landkreis", "landkreis_type", "state", "geometry"]

countries["lat"] = countries.geometry.apply(lambda x: x.centroid.y)
countries["lon"] = countries.geometry.apply(lambda x: x.centroid.x)
del countries["geometry"]

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

countries["country_id"] = "DE"
countries["country"] = "Deutschland"

countries = countries.merge(
  df_state_ids,
  on="state",
  how="left",
  suffixes=(False, False))


countries.to_sql(
  con=engine,
  name="locations",
  index=False,
  #schema=config["database"], # optional
  if_exists="append",
  chunksize=500, # rows at once
)
