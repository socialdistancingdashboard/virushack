""" This Script retrieves data from db and delivers spacial data for dashboard requests."""

import json
import pandas as pd
from datetime import datetime, timedelta
import re
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

config = json.load(open("credentials-aws-db.json", "r"))

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

def lambda_handler(event, context):
  q = """ SELECT * FROM locations """ 
  locations = pd.read_sql(q, aws_engine)
  locations = locations.drop("ts", axis=1)

  return {
    "statusCode": 200,
    "body": locations.to_json(orient="records")
  }



