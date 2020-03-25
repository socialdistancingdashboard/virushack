#!/usr/bin/env python
# coding: utf-8

# In[71]:


import json
from datetime import datetime, timedelta
import requests
import pandas as pd
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import dateutil.parser


# In[107]:


with open('kreise.json') as f:
    data_json = json.load(f)


# In[ ]:


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


# In[120]:


q = """
  SELECT locations.district_id 
  FROM locations
  WHERE district_id NOT IN (SELECT DISTINCT district_id FROM weather)
""" 
df_todoliste = pd.read_sql(q, aws_engine)


# In[138]:


today_date = datetime.today() + timedelta(-1)
start_date = datetime(2007,1,1)
WEATHER_API_KEY=#insert key here


data_df=pd.DataFrame()
for kreis in data_json: 
    if kreis['district_id'] in df_todoliste['district_id'].values:
        #start get weather data
        #-------------------------------------------------
        print(kreis['district'])
        weather_stations = requests.get(
            'https://api.meteostat.net/v1/stations/nearby?lat={}&lon={}&limit=20&key={}'.format(float(kreis['lat']),
                                                                                                float(kreis['lon']),
                                                                                                WEATHER_API_KEY))
        #loop over next stations if current station has no data for current day
        for station in weather_stations.json()['data']:
            #print('station_tried', station)
            closest_station = station['id']
            weather_data = requests.get(
                'https://api.meteostat.net/v1/history/daily?station={}&start={}&end={}&key={}'.format(closest_station,
                                                                                                      str(start_date).split()[0],
                                                                                                      str(today_date).split()[0],
                                                                                                      WEATHER_API_KEY
                                                                                                     ))
            #exit loop if current station already has data for current day
            if weather_data.json()['data'] and len(weather_data.json()['data']) > 365 and weather_data.json()['data'][-1]['date'] > '2020-01-01':
                break
        weather_data_entries = weather_data.json()['data']
        #--------------------------------------------------
        #end get weather data
        df = pd.DataFrame(data=weather_data_entries)
        df['district_id']=kreis['district_id']
        data_df = data_df.append(df)


# In[139]:


data_df = data_df.rename(columns={"date": "dt",
                          "temperature": "temp",
                          "temperature_min": "temp_min", 
                          "temperature_max": "temp_max",
                          "precipitation": "rainfall"
                         })


# In[143]:


data_df.to_sql(
  con=aws_engine,
  name="weather",
  index=False,
  #schema=config["database"], # optional
  if_exists="append", # wenn tabelle existiert anhängen oder löschen und ersetzen
  chunksize=500, # rows at once
)


# In[ ]:




