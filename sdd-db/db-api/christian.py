""" This Script retrieves data from db and delivers spacial data for dashboard requests."""​

try:
  if __IPYTHON__ : os.chdir(__file__)
except: pass

import json
import pandas as pd
from datetime import datetime, timedelta
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import dateutil.parser


config = json.load(open("credentials-aws-db.json", "r"))
​
aws_engine = create_engine(
    ("mysql+pymysql://" +
     config["user"] + ":" +
     config["password"] + "@" +
     config["host"] + ":" +
     str(config["port"]) + "/" +
     config["database"]),
    poolclass=NullPool,  # dont maintain a pool of connections
    pool_recycle=3600  # handles timeouts better, I think...
)
​ 
​
def on_error(e):
    return {
        "statusCode": 400,
        "body": "Bad Request: " + str(e)
    }
​
​
def lambda_handler(event, context):
    try:
        # assert "body" in event, "provide body"
        # event = json.loads(event["body"])

        # check user inputs and return error state if input is not valid
        assert "start" in event, "Provide a date as 'YYYY-MM-DD' (ISO 8601 extended format?)"
        assert "end" in event, "Provide a date as 'YYYY-MM-DD' (ISO 8601 extended format?)"
        assert "timeline_specs" in event, "Provide timeline specifications as an array of category, spatial_granularity and an array spatial_filter that cotains ids that should be filtered"
​
        assert type(event["timeline_specs"]
                    ) == list, "timeline-specs needs to be a list."
        assert len(event["timeline_specs"]
                   ) > 0, "timeline-specs may not be empty"
​
        for ts in event["timeline_specs"]:
            assert "category" in ts, "timeline_specs malformed."
            assert "spatial_granularity" in ts, "Please provide a spatial granularity identifier (1: country, 2: state, 3: district)"
            assert "spatial_filters" in ts, "timeline_specs malformed."
​
            assert type(
                ts["spatial_filters"]) == list, "timeline_specs malformed. Spatial filter needs to be a list."
​
        #  for sf in ts["spatial_filters"]:
        #    assert "spatial_id" in sf, "If spatial_filters is used, please provide an array of spatial_ids as strings."
    except Exception as e:
        return on_error(e)
​
    spatial_id_lookup = {
        1: "country",
        2: "state",
        3: "district"
    }
​
    # get categories meta information
    # q = "SELECT * FROM categories"
    # df_categories = pd.read_sql(q, aws_engine)
​
    #  ts = event["timeline_specs"][0]
​
    start = dateutil.parser.isoparse(event["start"])
    end = dateutil.parser.isoparse(event["end"])
    timelines = []
    for ts in event["timeline_specs"]:
        category = ts["category"]
        spatial_granularity = ts["spatial_granularity"]
        spatial_filters = ts["spatial_filters"]
​
        spatial = spatial_id_lookup[spatial_granularity]
​
        timeline = {
            "category": category,
            "spatial_granularity": spatial_granularity,
            "spatial_filters": spatial_filters,
        }
​
        q = """
            SELECT *
            FROM measures
            """  # % (start, end)
        # WHERE measures.dt_start_action >= '%s'
        # AND measures.dt_start_action < '%s'
​
        if len(spatial_filters) > 0:
            q_spatial_filters = ",".join(
                ["'" + sf + "'" for sf in spatial_filters])
            q = q + ("WHERE measures.%s_id_action in (%s) " %
                     (spatial, q_spatial_filters))
​
        # q = q + """
        #  GROUP BY measures.dt_start_action
        # """
​
        df = pd.read_sql(q.replace("%", "%%"), aws_engine)
​
        df = df.astype({"dt_announcement": 'datetime64[ns]',
                        "dt_start_action": 'datetime64[ns]',
                        "dt_end_action": 'datetime64[ns]'}, errors='ignore')
        df.dt_end_action = pd.to_datetime(df.dt_end_action, errors='coerce')
​
        df = df[(df["dt_start_action"] >= start)]
        df = df[(df["dt_end_action"] < end)]
        #df.date = df.date.apply(lambda x: x.isoformat())
​
        timeline["values"] = json.loads(df.to_json(orient="records"))
        timelines.append(timeline)
​
    result = {
        "request": {
            "start": start.isoformat(),
            "end": str(end.isoformat()),
            "timeline_specs": event["timeline_specs"]
        },
        "timelines": timelines
    }
​
    result
​
    return {
        "statusCode": 200,
        "body": json.dumps(result),
    }
​
​
print(lambda_handler(event, None))