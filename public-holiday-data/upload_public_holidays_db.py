import holidays
import numpy as np
import dateutil.parser
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import requests
from datetime import datetime, timedelta
import json

config = json.load(open("../credentials/credentials-aws-db.json", "r"))
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
q = """
  SELECT distinct(state_id), state
  FROM locations
"""
# get all locations with missing data
df_todoliste = pd.read_sql(q, aws_engine)

# run this script at end of calendar year to get public holidays for next year
relevant_year = datetime.today().year + 1

germany_public_holidays = []
for index, row in df_todoliste.iterrows():
    # start get public holiday data for state
    # -------------------------------------------------
    for date in holidays.DE(years=np.arange(relevant_year, relevant_year + 5), prov=row['state_id']):
        germany_public_holidays.append([str(date), row['state_id']])
    # end get public holiday data for state
    # -------------------------------------------------

# upload data to db
with aws_engine.connect() as cnx:
    q = """
        REPLACE INTO holidays (dt, state_id)
        VALUES(%s,%s)
    """
    cnx.execute(q, germany_public_holidays , multi=True)
