""" Uploads Corona data from Zeit online
Note: infected numbers are known infections on a particular day.
Dead and Recovered numbers were summed up until today. """

import os
import pandas as pd
from datetime import datetime, timedelta
import pytz
# compatibility with ipython
try:
  __IPYTHON__
  os.chdir(os.path.dirname(__file__))
except: pass
import json
import pymysql
from pymysql.constants import CLIENT
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import requests

# connect to aws database with sqlalchemy (used for pandas connections)
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

# aws database connection used for normal queries because sqlalchemy doesnt support on duplicate key queries
pymysql_con = pymysql.connect(
  config["host"],
  config["user"],
  config["password"],
  config["database"],
  client_flag=CLIENT.MULTI_STATEMENTS)

charts_whitelist = [
  "import balance",
  "load",
  "day ahead auction",
  "intraday continuous average price",
  "intraday continuous id3 price",
  "intraday continuous id1 price"
]

description_lookup = {
  "import balance": {
    "desc_short": "Netto Stromimporte",
    "desc_long": "Netto Stromimporte",
    "unit": "Gigawatt",
    "unit_agg": "Gigawatt",
    "agg_mode": "sum"
  },
  "load": {
    "desc_short": "Stromverbrauch",
    "desc_long": "Stromverbrauch",
    "unit": "Gigawatt",
    "unit_agg": "Gigawatt",
    "agg_mode": "sum"
  },
  "day ahead auction": {
    "desc_short": "Day-ahead Strompreis",
    "desc_long": "Day-ahead Strompreise",
    "unit": "EUR/MWh",
    "unit_agg": "Prozent",
    "agg_mode": "avg-percentage-of-normal"
    },
  "intraday continuous average price": {
    "desc_short": "Strompreis Index IDFull",
    "desc_long": "The IDFull index is the weighted average price of all continuous trades executed during the full trading session of any EPEX SPOT continuous contract. This index includes the entire market liquidity and thus represents the obvious continuous market price references for each contract.",
    "unit": "EUR/MWh",
    "unit_agg": "Prozent",
    "agg_mode": "avg-percentage-of-normal"
  },
  "intraday continuous id3 price": {
    "desc_short": "Strompreis Index ID3",
    "desc_long": "The ID3 index is the weighted average price of all continuous trades executed within the last 3 trading hours of a contract (up to 30min before delivery start).This index focuses on the most liquid timeframe of a continuous contract trading session. As such, this index presents large business interest for EPEX SPOT customers to market their offers or challenge their trading activity.",
    "unit": "EUR/MWh",
    "unit_agg": "Prozent",
    "agg_mode": "avg-percentage-of-normal"
    },
  "intraday continuous id1 price": {
    "desc_short": "Strompreis Index ID1",
    "desc_long": "The ID1 index is the weighted average price of all continuous trades executed within the last trading hour of a contract up to 30min before delivery start. This index catches the market last minute imbalance needs, reflecting amongst other the increasing REN breakthrough and system balancing flexibility.",
    "unit": "EUR/MWh",
    "unit_agg": "Prozent",
    "agg_mode": "avg-percentage-of-normal"
  }
}

# retrieve data from fraunhofer ise


def upload_week(week):
  url = f"https://www.energy-charts.de/price/week_2020_{week}.json"
  r = requests.get(url)
  data = r.json()
  for chart in data:
    chart_key = chart["key"][0]["en"].lower().replace("-", " ")
    if not chart_key in charts_whitelist:
      continue

    print(f"current chart_key {chart_key}")

    source_id = ("score fraunhofer " + chart_key).replace(" ", "_")

    source = {
      "id": source_id,
      "desc_short": description_lookup[chart_key]["desc_short"],
      "desc_long": description_lookup[chart_key]["desc_long"] ,
      "contributors": "Fraunhofer ISI, 50 Hertz, Amprion, Tennet, TransnetBW, EEX, EPEX SPOT",
      "unit": description_lookup[chart_key]["unit"],
      "unit_long": description_lookup[chart_key]["unit"],
      "unit_agg_long": description_lookup[chart_key]["unit_agg"],
      "sample_interval": "hourly",
      "agg_mode": description_lookup[chart_key]["agg_mode"],
      "has_reference_values": 0,
      "spatial_level": "country"
    }

    station = {
      "source_id": source_id,
      "description": "country-level data",
      "source_station_id": "country-level data",
      "spatial_id": "DE"
    }

    q = """
      REPLACE INTO sources (
        id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long,
        sample_interval, agg_mode, has_reference_values, spatial_level )
      VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with pymysql_con.cursor() as cur:
      cur.execute(q, list(source.values()))
    pymysql_con.commit()

    q = """
      INSERT INTO stations ( source_id, description, source_station_id, spatial_id )
      VALUES ( %s, %s, %s, %s )
      ON DUPLICATE KEY UPDATE
      source_id = VALUES(source_id),
      description = VALUES(description),
      source_station_id = VALUES(source_station_id),
      spatial_id = VALUES(spatial_id)
    """
    with pymysql_con.cursor() as cur:
      cur.execute(q, list(station.values()))
    pymysql_con.commit()

    q = """
      SELECT id AS station_id, spatial_id FROM stations
      WHERE source_id = '%s'
    """ % source_id

    scores_stations_foreign_keys = pd.read_sql(q, aws_engine)

    # remove trailing zeros
    drop_index = len(chart["values"])
    while chart["values"][drop_index-1][1] == 0:
      drop_index = drop_index - 1

    df_scores = pd.DataFrame(chart["values"][:drop_index], columns=["dt", "score_value"])
    df_scores.dropna(inplace=True)
    df_scores.dt = df_scores.dt.apply(lambda x: datetime.fromtimestamp(x / 1000))
    df_scores['dt'] = df_scores['dt'].astype(str)
    df_scores["spatial_id"] = "DE"
    df_scores["source_id"] = source_id

    df_scores = df_scores.merge(
      scores_stations_foreign_keys,
      on="spatial_id",
      how="left",
      suffixes=(False, False)
    )

    q = """
      INSERT INTO scores ( dt, score_value, source_id, spatial_id, station_id )
      VALUES (%s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
      score_value = VALUES(score_value)
    """

    with pymysql_con.cursor() as cur:
      cur.executemany(q, df_scores[["dt", "score_value", "source_id", "spatial_id", "station_id"]].values.tolist())
    pymysql_con.commit()

  print("uploaded week %s done" % week)

def upload_all():
  """ Drop all fraunhofer data before reuploading """

  q = """
    DELETE FROM sources WHERE id LIKE '%fraunhofer%';
    DELETE FROM stations WHERE source_id LIKE '%fraunhofer%';
    DELETE FROM scores WHERE source_id LIKE '%fraunhofer%';
  """
  with pymysql_con.cursor() as cur:
    cur.execute(q)
  pymysql_con.commit()

  start = datetime(2020,1,1)
  week = start.isocalendar()[1]
  current_week = datetime.now().isocalendar()[1]

  while week <= current_week:
    upload_week(str(week).zfill(2))
    week = week + 1

# upload_all()

# upload for today
current_week = datetime.now().isocalendar()[1]
upload_week(str(week).zfill(2))


pymysql_con.close()