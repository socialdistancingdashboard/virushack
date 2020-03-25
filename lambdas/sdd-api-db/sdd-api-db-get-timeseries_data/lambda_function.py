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
event = {
  "start": "2020-01-27",
  "end": "2020-01-28",
  "timeline_specs": [{
      "category": "score_public_transportation_regional",
      "spatial_granularity": 3,
      "spatial_filter": []
    }
  ]
}

def on_error(e):
 return {
  "statusCode": 400,
  "body": "Bad Request: " + str(e)
 }

def lambda_handler(event, context):
  try:
    # check user inputs and return error state if input is not valid
    assert "start" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "end" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "timeline_specs" in event, "Provide timeline specifications as an array of category, spatial_granularity and an array spatial_filter that cotains ids that should be filtered"

    assert type(event["timeline_specs"]) == list, "timeline-specs needs to be a list."
    assert len(event["timeline_specs"]) > 0, "timeline-specs may not be empty"

    for ts in event["timeline_specs"]:
      assert "category" in ts, "timeline_specs malformed."
      assert "spatial_granularity" in ts, "Please provide a spatial granularity identifier (1: country, 2: state, 3: district)"
      assert "spatial_filter" in ts, "timeline_specs malformed."

      assert type(ts["spatial_filter"]) == list, "timeline_specs malformed. Spatial filter needs to be a list."

      for sf in ts["spatial_filter"]:
        assert "spatial_id" in sf, "If spatial_filter is used, please provide an array of spatial_ids as strings."
  except Exception as e:
    return on_error(e)

  spatial_id_lookup = {
    1: "country",
    2: "state",
    3: "district"
  }

  # get categories meta information
  q = "SELECT * FROM categories"
  df_categories = pd.read_sql(q, aws_engine)    


  for ts in event["timeline_specs"]:
    category = ts["category"]
    spatial_granularity = ts["spatial_granularity"]
    spatial_filter = ts["spatial_filter"]

    q_filter = ",".join(spatial_filter)
    spatial = spatial_id_lookup[param_spatial_granularity]


    q = """
      SELECT 
        SUM(score_value) AS score, 
        locations.%s_id AS spatial_id,
        locations.%s AS spatial_name,
        category
      FROM scores
      JOIN locations ON scores.district_id = locations.district_id
      WHERE scores.dt >= '%s' 
      AND scores.dt < '%s'
      AND category = %s
      GROUP BY spatial_id, category
    """ % (spatial_id, param_start, param_end, q_categories)


  df = pd.read_sql(q, aws_engine)
  result = {
    "request": {
      "date": event["date"],
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



