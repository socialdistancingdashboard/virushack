""" This Script retrieves data from db and delivers spacial data for dashboard requests."""

import json
import pandas as pd
from datetime import datetime, timedelta
import re
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import dateutil.parser

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

# use this for testing
# event = {
#   "start": "2020-01-27",
#   "end": "2020-01-28",
#   "categories": ["score_public_transportation_regional"],
#   "spatial_granularity": 3
# }


# event = {
#   "start": "2020-01-27",
#   "end": "2020-03-28",
#   "categories": [
#     "score_public_transportation_all",
#     "score_public_transportation_all",
#   ],
#   "spatial_granularity": 3
# }

def on_error(e):
 return {
  "statusCode": 400,
  "body": "Bad Request: " + str(e)
 }

def lambda_handler(event, context):

  try:
    assert "body" in event, "provide body"
    event = json.loads(event["body"])

      # check user inputs and return error state if input is not valid
    assert "categories" in event, "Please provide cateogries as array"
    assert "start" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "end" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "spatial_granularity" in event, "Please provide a spatial granularity identifier (1: country, 2: state, 3: district)"

    param_start = event["start"]
    param_end = event["end"]
    param_categories = event["categories"]
    param_spatial_granularity = event["spatial_granularity"]

    param_start = dateutil.parser.isoparse(param_start)
    param_end = dateutil.parser.isoparse(param_end)
    assert type(param_categories) == list, "Please provide a list of categories."
    assert len(param_categories) > 0, "Please provide at least one category. Found type " + str(type(param_categories))
    assert type(param_spatial_granularity) == int, "Please provide spatial_granularity as integer values"
    assert param_spatial_granularity >= 1, "Please provide a spatial_granularity value greater or equal 1."
    assert param_spatial_granularity <= 3, "Please provide a spatial_granularity value of less or equal 3"
  except Exception as e:
    return on_error(e)


  q_categories = ",".join(["'" + c + "'" for c in  param_categories])

  spatial_id_lookup = {
    1: "country_id",
    2: "state_id",
    3: "district_id"
  }
  spatial_id = spatial_id_lookup[param_spatial_granularity]

  q = """
    SELECT 
      AVG(score_value) AS score, 
      locations.%s AS spatial_id, 
      category
    FROM scores
    JOIN locations ON scores.district_id = locations.district_id
    WHERE scores.dt >= '%s' 
    AND scores.dt < '%s'
    AND category IN (%s)
    GROUP BY spatial_id, category
  """ % (spatial_id, param_start, param_end, q_categories)

  df = pd.read_sql(q, aws_engine)

  result = {
    "request": {
      "start": event["start"],
      "end": event["end"],
      "categories": event["categories"],
      "spatial_granularity": event["spatial_granularity"]
    },
    "data": []
  }

  for category in param_categories:
    df_filtered = df[df.category == category]
    result["data"].append({
      "category": category,
      "values": json.loads(df_filtered[["score", "spatial_id"]].to_json(orient="records"))
    })

  return {
    "statusCode": 200,
    "body": json.dumps(result),
  }

# lambda_handler(event, None)



