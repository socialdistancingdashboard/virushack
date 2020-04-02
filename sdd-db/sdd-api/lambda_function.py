
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
  "statusCode": 200,
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
    on_error(e)


def get_station_data(event, context):
  try:
    assert event['httpMethod'] == 'GET', "Use GET for this request"

    source_id = event['pathParameters']['source_id']
    assert source_id != "", "please provide a source_id"
    
    query = """
        SELECT 
          T1.dt, 
          T1.score_value, 
          T1.reference_value, 
          T1.source_id, 
          T1.district_id, 
          T1.station_id, 
          T2.source_station_id
        FROM scores AS T1
        JOIN stations AS T2 ON T2.id = T1.station_id
        WHERE T1.station_id = '%s'
    """ % (source_id)

    df = pd.read_sql(query, aws_engine ) #,  params=(start_date, end_date))
    df["dt"] = df["dt"].astype(str) # transform to datestring to avoid any timezone information when exporting to json
    return {
      'statusCode': 200,
      'headers': {
        'access-control-allow-methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT',
        'access-control-allow-origin': '*',
        "Access-Control-Allow-Headers": 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
      },
      "body": df.to_json(force_ascii=False, orient="records",  date_format = "iso"),
    }   
  except Exception as e:
    on_error(e)
    
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
    on_error(e)


def get_stations(event, context):
  try:
    assert event['httpMethod'] == 'GET', "Use GET for this request"

    query = """
      SELECT T1.source_id, T1.id, T1.description, T2.district_id, T2.district, T2.state_id, T2.state, T2.country_id, T2.country
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
    on_error(e)


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
    on_error(e)
  
