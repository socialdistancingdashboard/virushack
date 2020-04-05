
import json
import pandas as pd
from datetime import datetime, timedelta
import re
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
try:  
  __IPYTHON__
  os.chdir(os.path.dirname(__file__))
except: pass

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

def on_error(e):
  return {
  "statusCode": 500,
  "body": json.dumps(str(e)),
  'headers': {
    'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
    'access-control-allow-origin': '*',
    "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
  }
}

def template(event, context):
  try:
    query = """"""

    df = pd.read_sql(query, aws_engine ) #,  params=(start_date, end_date))
      
    assert event['httpMethod'] == 'GET', "Use GET for this request"
    
    params = json.loads(event["body"])

    return {
      'statusCode': 200,
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      "body": df.to_json( force_ascii=False, orient="records"),
    }   
  except Exception as e:
    return on_error(e)

def post_test(event, context):
  try:
    result = {
      "httpmethod": event['httpMethod'],
      "params": event["body"]
    }
    raise "nananan so nicht"
  except:
    return on_error("geeeeht nicht")

  return {
    'statusCode': 200,
    'headers': {
      'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
      'access-control-allow-origin': '*',
      "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    },
    "body": json.dumps(result)
  }   

def get_station_data(event, context):
  try:
    assert event['httpMethod'] == 'POST', "Use POST for this request"
    assert event["body"], "Please provide body with parameters."
    params = json.loads(event["body"])

    #params = {"source_id": "score_google_places"}
    

    assert "source_id" in params, "please provide a source_id"
    source_id = params["source_id"] if "source_id" in params else None
    state_id = params["state_id"] if "state_id" in params else None
    district_id = params["district_id"] if "district_id" in params else None
    station_id = params["station_id"] if "station_id" in params else None
    params["country_id"] = "DE"

    agg_level = "station"
    if not station_id:
      agg_level = "district"
    if not district_id:
      agg_level = "state"
    if not state_id:
      agg_level = "country"
    
    
    # load all information for the requested source
    source = pd.read_sql("SELECT * FROM sources WHERE id = '%s'" % source_id, aws_engine ) 
    assert len(source) == 1, "Please provide correct source_id."
    source_corona = pd.read_sql("SELECT * FROM sources WHERE id = 'corona_infected'", aws_engine ) 

    meta = {
      "yaxis0": {
        "ylabel": source.unit.iloc[0],
        "desc_short": source.desc_short.iloc[0],
        "desc_long": source.desc_long.iloc[0],
        "mode": source["mode"].iloc[0],
        "agg_level": agg_level,
        "agg_level_id": params[agg_level + "_id"],
        "agg_mode": "avg-percentage-of-normal"
      }
    }

    # used to autogenerate mysql-query
    filters = [
      # ("T3.country_id", "DE"),
      ("T3.state_id", state_id),
      ("T3.district_id", district_id),
      ("T1.station_id", station_id)
    ]

    # used to auto-generate mysql-query
    q_filter = " AND ".join([ "%s='%s'" % (name, val) for name, val in filters  if val])
    q_filter = " AND " + q_filter if q_filter else ""

    query = """
      SELECT 
        T1.dt, 
        AVG(T1.score_value / T1.reference_value) AS score
      FROM scores AS T1
      JOIN locations AS T3 ON T1.district_id = T3.district_id
      WHERE T1.source_id = '%s'
        %s
      GROUP BY dt
      ORDER BY T1.dt ASC
    """ % (source_id, q_filter)

    #print('(pymysql.err.ProgrammingError) (1064, \"You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near \'FROM scores AS T1\\n        JOIN stations AS T2 ON T2.id = T1.station_id\\n        J\' at line 4\")\n[SQL: \n        SELECT \n          T1.dt, \n          AVG(T1.reference_value / T1.score_value),\n        FROM scores AS T1\n        JOIN stations AS T2 ON T2.id = T1.station_id\n        JOIN locations AS T3 ON T2.district_id = T3.district_id\n        WHERE T2.source_id = \'score_google_places\'\n         \n          GROUP BY dt \n        ORDER BY T1.dt ASC\n        \n    ]\n(Background on this error at: http://sqlalche.me/e/f405)')
    print(query)
    
    # retrieve data
    df = pd.read_sql(query, aws_engine )

    query = """
      SELECT 
        T1.dt, 
        SUM(T1.score_value) AS score
      FROM scores AS T1
      JOIN locations AS T3 ON T1.district_id = T3.district_id
      WHERE T1.source_id = 'corona_infected'
        %s
      GROUP BY dt
      ORDER BY T1.dt ASC
    """ % (q_filter,)
    
    # retrieve corona data
    df_corona = pd.read_sql(query, aws_engine)

    meta["yaxis1"] = {
      "ylabel": source_corona.unit.iloc[0],
      "desc_short": source_corona.desc_short.iloc[0],
      "desc_long": source_corona.desc_long.iloc[0],
      "mode": source_corona["mode"].iloc[0],
      "agg_level": agg_level,
      "agg_level_id": params[agg_level + "_id"],
      "agg_mode": "sum"
    }

    # transform to datestring to avoid any timezone information when exporting to json
    df["dt"] = df["dt"].astype(str) 
    df_corona["dt"] = df_corona["dt"].astype(str)

    result = {
      "meta": meta,
      "data": json.loads(df.to_json(force_ascii=False, orient="records",  date_format = "iso")),
      "corona": json.loads(df_corona.to_json(force_ascii=False, orient="records",  date_format = "iso")),
    }

    return {
      'statusCode': 200,
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      "body": json.dumps(result)
    }   
  except Exception as e:
    return on_error(e)
    
def get_locations(event, context):
  try:
    assert event['httpMethod'] == 'GET', "Use GET for this request"
    q = """
      SELECT 
        district_id,
        district,
        state_id,
        state,
        country_id,
        country
      FROM locations
    """ 

    locations = pd.read_sql(q, aws_engine)

    states = locations.groupby('state_id').apply(lambda x: x.iloc[0])
    states = states.drop(["district_id", "district"], axis=1)

    countries = states.groupby('country_id').apply(lambda x: x.iloc[0])
    countries = countries.drop(["state_id", "state"], axis=1)

    result = {
      "countries": countries.to_dict(orient="records"),
      "states": states.to_dict(orient="records"),
      "districts": locations.to_dict(orient="records")
    }

    return {
      'statusCode': 200,
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      'body': json.dumps(result)
    }   
  except Exception as e:
    return on_error(e)


def get_stations(event, context):
  try:
    assert event['httpMethod'] == 'GET', "Use GET for this request"

    query = """
      SELECT T1.source_id, T1.id, T1.description, T2.district_id, T2.district, T2.district_type, T2.state_id, T2.state, T2.country_id, T2.country
      FROM stations AS T1
      JOIN locations AS T2 ON T1.district_id = T2.district_id
    """

    df = pd.read_sql(query, aws_engine ) #,  params=(start_date, end_date))
    
    return {
      "statusCode": 200,
      "body": df.to_json(force_ascii=False, orient="records"),
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      }
    }
  except Exception as e:
    return on_error(e)


def get_sources(event, context):
  try:
    assert event['httpMethod'] == 'GET', "Use GET for this request"

    query = """
      SELECT id, desc_short, desc_long 
      FROM sources
    """

    df = pd.read_sql(query, aws_engine ) #,  params=(start_date, end_date))
    
    return {
      "statusCode": 200,
      "body": df.to_json(force_ascii=False,orient="records"),
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      }
    }
  except Exception as e:
    return on_error(e)
  

def get_station_data_OLD(event, context):
  # def has_references(df):
  #   """ returns True if all(!) reference values exist """
  #   return df["reference_value"].isna().sum() == 0

  # def predictable(df):
  #   """ Returns true if history is older than 2020-01-01 """
  #   return df.dt.min() < datetime(2020,1,1)

  # def predict(df):
  #   """ return a series of predictions """
  #   for column in ["dt", "score_value"]:
  #     assert column in df, "Please provide '%s' for prediction." % column
  #   df["prediction"] = 1
  #   return df["prediction"]

  # def aggregate(df, meta):
  #   """ aggregates the queried data and guarantees statistical correctness """
  #   available_modes = ["sum", "avg-percentage-of-normal"]
  #   assert meta["agg_mode"] in available_modes, "Please provide a correct aggregation mode. Found '%s', expected %s." % (column, str(available_modes))

  #   if meta["agg_mode"] == "sum":
  #     raise NotImplementedError("agg_mode 'sum' not implemented")

  #   if meta["agg_mode"] == "avg-percentage-of-normal":
  #     if meta["agg_level"] == "station":
  #       # return raw for debugging
  #       df["score"] = df["score_value"]
  #       return df[["dt", "score"], meta]
  #     else:
  #       df["score"] = df["score_value"] / df["reference_value"]
  #       # df["spatial_id"] = df[meta["agg_level"]+"_id"]
  #       # df = df[["dt", "score", "spatial_id"]]
  #       meta["ylabel"] = "Abweichung vom Normalwert" % meta["ylabel"]
  #       meta["example"] = "Eine Wert von 0.5 entspricht der Hälfte des Normalwertes."
  #       return df.groupby(by=["dt"], as_index=False).mean()[["dt", "score"]], meta


  try:
    assert event['httpMethod'] == 'POST', "Use POST for this request"
    # source_id = event['pathParameters']['source_id']
    
    params = json.loads(event["body"])

    assert "source_id" in params, "please provide a source_id"
    source_id = params["source_id"] if "source_id" in params else None
    state_id = params["state_id"] if "state_id" in params else None
    district_id = params["district_id"] if "district_id" in params else None
    station_id = params["station_id"] if "station_id" in params else None
    params["country_id"] = "DE"

    agg_level = "station"
    if not station_id:
      agg_level = "district"
    if not district_id:
      agg_level = "state"
    if not state_id:
      agg_level = "country"
    
    # agg_to_words = {
    #   "station": "der Messstation",
    #   "district": "auf Ebene der Kreise",
    #   "state": "auf Ebene der Bundesländer",
    #   "nation": "für ganz Deutschland"
    # }

    # load all information for the requested source
    source = pd.read_sql("SELECT * FROM sources WHERE id = '%s'" % source_id, aws_engine ) 
    assert len(source) == 1, "Please provide correct source_id."

    # if has_references(df):
    #   df, meta = aggregate(df, meta)
    # else:
    #   if predictable(df):
    #     raise NotImplementedError("no predictions right now")
    #     # df[reference_value] = predict(df)
    #     # df, meta = aggregate(df, meta)
    #   else:
    #     raise("Darstellung %s nicht möglich, da nicht genügend historische Daten zur Verfügung stehen. Diese werden aber benötigt, um Messstationen %s zu vergleichen. Wähle bitte nachfolgend eine einzelne Messstation aus, um deren Daten angezeigt zu bekommen." % ((agg_to_words[agg_level],)*2))

    meta = {
      "ylabel": source.unit.iloc[0],
      "desc_short": source.desc_short.iloc[0],
      "desc_long": source.desc_long.iloc[0],
      "mode": source["mode"].iloc[0],
      "agg_level": agg_level,
      "agg_level_id": params[agg_level + "_id"],
      "agg_mode": "avg-percentage-of-normal"
    }

    # used to autogenerate mysql-query
    filters = [
      # ("T3.country_id", "DE"),
      ("T3.state_id", state_id),
      ("T3.district_id", district_id),
      ("T1.station_id", station_id)
    ]

    # used to auto-generate mysql-query
    q_filter = " AND ".join([ "%s='%s'" % (name, val) for name, val in filters  if val])
    q_filter = " AND " + q_filter if q_filter else ""

    # q_group = "" # tbd

    query = """
      SELECT 
        T1.dt, 
        AVG(T1.reference_value / T1.score_value),
      FROM scores AS T1
      JOIN stations AS T2 ON T2.id = T1.station_id
      JOIN locations AS T3 ON T2.district_id = T3.district_id
      WHERE T2.source_id = '%s'
        %s
      ORDER BY T1.dt ASC
    """ % (source_id, q_filter)

    # retrieve data
    df = pd.read_sql(query, aws_engine )

    df["dt"] = df["dt"].astype(str) # transform to datestring to avoid any timezone information when exporting to json

    result = {
      "meta": meta,
      "data": df.to_json(force_ascii=False, orient="records",  date_format = "iso"),
    }

    return {
      'statusCode': 200,
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      "body": json.dumps(result)
    }   
  except Exception as e:
    return on_error(e)