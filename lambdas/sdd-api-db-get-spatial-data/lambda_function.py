import json
import pandas as pd
import pymysql
from datetime import datetime
import re


config = json.load(open("sdd-db.conf", "r"))

# Connect to the database.
connection = pymysql.connect(
  host=config["host"],
  user=config["user"],
  password=config["password"],                             
  db=config["database"],
  charset='utf8',
  cursorclass=pymysql.cursors.DictCursor)


pattern_date = re.compile(r"^\d\d\d\d-\d\d-\d\d$")

def on_error(e):
 return {
 "statusCode": 400,
 "body": "Bad Request: " + str(e)
 }

def lambda_handler(event, context):
 param_date = event["date"]
 param_categories = event["categories"]
 param_spatial_granularity = event["spatial_granularity"]
 
 try:
  assert re.match(pattern_date, param_date) != None, "Please provide date as YYYY-MM-DD"
  #param_date = datetime.strptime(param_date, '%Y-%m-%d')
  assert type(param_categories) == list, "Please provide a list of categories."
  assert len(param_categories) > 0, "Please provide at least one category. Found type " + str(type(param_categories))
  assert type(param_spatial_granularity) == int, "Please provide spatial_granularity as integer values"
  assert param_spatial_granularity >= 1, "Please provide a spatial_granularity value greater or equal 1."
  assert param_spatial_granularity <= 3, "Please provide a spatial_granularity value of less or equal 3"
 except Exception as e:
  return on_error(e)
  

 return {
 "statusCode": 200,
 "body": json.dumps({
     "message": "hello world" + str(param_date)
 }),
}
