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
#   "timeline_specs": [{
#       "category": "score_public_transportation_regional",
#       "spatial_granularity": 3,
#       "spatial_filters": []
#     }, {
#       "category": "score_public_transportation_all",
#       "spatial_granularity": 2,
#       "spatial_filters": ["SN", "BW", "B"]
#     }

#   ]
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
    assert "start" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "end" in event, "Provide a date as 'YYYY-MM-DDTHH:MM:SS' (ISO 8601 extended format)"
    assert "timeline_specs" in event, "Provide timeline specifications as an array of category, spatial_granularity and an array spatial_filter that cotains ids that should be filtered"

    assert type(event["timeline_specs"]) == list, "timeline-specs needs to be a list."
    assert len(event["timeline_specs"]) > 0, "timeline-specs may not be empty"

    for ts in event["timeline_specs"]:
      assert "category" in ts, "timeline_specs malformed."
      assert "spatial_granularity" in ts, "Please provide a spatial granularity identifier (1: country, 2: state, 3: district)"
      assert "spatial_filters" in ts, "timeline_specs malformed."

      assert type(ts["spatial_filters"]) == list, "timeline_specs malformed. Spatial filter needs to be a list."

    #  for sf in ts["spatial_filters"]:
    #    assert "spatial_id" in sf, "If spatial_filters is used, please provide an array of spatial_ids as strings."
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

#  ts = event["timeline_specs"][0]

  start = dateutil.parser.isoparse(event["start"])
  end = dateutil.parser.isoparse(event["end"])
  timelines = []
  for ts in event["timeline_specs"]:
    category = ts["category"]
    spatial_granularity = ts["spatial_granularity"]
    spatial_filters = ts["spatial_filters"]

   
    spatial = spatial_id_lookup[spatial_granularity]

    timeline = {
      "category": category,
      "description_short": df_categories[df_categories.name == category].desc_short.values[0],
      "description_long": df_categories[df_categories.name == category].desc_long.values[0],
      "spatial_granularity": spatial_granularity,
      "spatial_filters": spatial_filters,
    }

    q = """
      SELECT 
        DATE_FORMAT(dt, '%%Y-%%m-%%dT%%TZ') AS datetime,
        AVG(score_value) AS score
      FROM scores
      JOIN locations ON scores.district_id = locations.district_id
      WHERE category = '%s'
      AND scores.dt >= '%s'
      AND scores.dt < '%s'
    """ % (category, start, end)

    if len(spatial_filters ) > 0:
      q_spatial_filters = ",".join(["'" + sf + "'" for sf in spatial_filters])
      q = q + (" AND locations.%s_id in (%s) " % (spatial, q_spatial_filters))

    q = q + """
      GROUP BY scores.dt
    """

    df = pd.read_sql(q.replace("%", "%%"), aws_engine)
    df["prediction"] = 0
    
    #df.date = df.date.apply(lambda x: x.isoformat())

    timeline["values"] = json.loads(df.to_json(orient="records"))
    timelines.append(timeline)

  result = {
    "request": {
      "start": start.isoformat(),
      "end": str(end.isoformat()),
      "timeline_specs": event["timeline_specs"]
    },
    "timelines": timelines
  }

  result

  return {
    "statusCode": 200,
    "body": json.dumps(result),
  }

# lambda_handler(event, None)



