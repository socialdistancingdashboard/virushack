import json
import pandas as pd
import pymysql

config = json.load(open("sdd-db.conf", "r"))

# Connect to the database.
connection = pymysql.connect(
  host=config["host"],
  user=config["user"],
  password=config["password"],                             
  db=config["database"],
  charset='utf8',
  cursorclass=pymysql.cursors.DictCursor)


def lambda_handler(event, context):
  query = """
    SELECT name, desc_short, desc_long 
    FROM categories
  """
  df = pd.read_sql(query, connection ) #,  params=(start_date, end_date))
  
  return {
    "statusCode": 200,
    "body": df.to_json(
      force_ascii=False,
      orient="records")
  }

