#!/usr/bin/env python
# coding: utf-8

# In[36]:


import json
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import boto3
import requests
import json
from datetime import datetime, timedelta


# In[37]:


pratiques_path = "pratiques.csv"
locations_path = "Counterlist-DE.csv"
pratiques_df = pd.read_csv(pratiques_path,sep='\t')
locations_df = pd.read_csv(locations_path,sep='\t')


# In[38]:


province_abbs = {
    'Baden-Württemberg' : 'BW',
    'Bayern' : 'BY',
    'Berlin' : 'BE',
    'Brandenburg' : 'BB',
    'Bremen' : 'HB',
    'Hamburg' : 'HH',
    'Hessen' : 'HE',
    'Mecklenburg-Vorpommern' : 'MV',
    'Niedersachsen' : 'NI',
    'Nordrhein-Westfalen' : 'NW',
    'Rheinland-Pfalz' : 'RP',
    'Saarland' : 'SL',
    'Sachsen' : 'SN',
    'Sachsen-Anhalt' : 'ST',
    'Schleswig-Holstein' : 'SH',
    'Thüringen' : 'TH'
}


# In[51]:


from geopy.geocoders import Nominatim
import holidays
from prediction import BikePrediction

today_date = datetime.today()
yesterday_date = today_date - timedelta(1)

def create_request():
    json_data={}
    data_sets = []
    BP = BikePrediction()
  
    for index, row in locations_df.iterrows():
        #print('index', index)
        url = 'http://data.eco-counter.com/ParcPublic/CounterData'
        
        yesterday_day, yesterday_month, yesterday_year = yesterday_date.day, yesterday_date.month, yesterday_date.year
        today_day, today_month, today_year = today_date.day, today_date.month, today_date.year
        
        
        #start get bike count data
        #------------------------------------------------
        pratiques = ""
        if hasattr(row, 'pratiques'):
            pratiques="&pratiques="+row.pratiques
        body = "idOrganisme=4586&idPdc={}&fin={}%2F{}%2F{}&debut={}%2F{}%2F{}&interval=4&pratiques={}".format(row.idPdc, today_day, today_month, today_year, yesterday_day, yesterday_month, yesterday_year, pratiques)

        headers = {
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "115",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "i18next=en_US; _ga=GA1.2.1682226698.1584790632; _gid=GA1.2.220973166.1584790632",
            "Host": "data.eco-counter.com",
            "Origin": "http://data.eco-counter.com",
            "Referer": "http://data.eco-counter.com/ParcPublic/?id=4586",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        bike_count_data = requests.post(url, body, headers=headers) 
        #no data available for location on current day
        if not bike_count_data.json()[:-1]:
            continue
        bike_count_data_entry = bike_count_data.json()[:-1][0]
        #-------------------------------------------------
        #end get bike count data
        
        
        #start get weather data
        #-------------------------------------------------
        weather_stations = requests.get(
            'https://api.meteostat.net/v1/stations/nearby?lat={}&lon={}&limit=20&key={}'.format(row.lat,
                                                                                                row.lon,
                                                                                                WEATHER_API_KEY))
        #loop over next stations if current station has no data for current day
        for station in weather_stations.json()['data']:
            #print('station_tried', station)
            closest_station = station['id']
            weather_data = requests.get(
                'https://api.meteostat.net/v1/history/daily?station={}&start={}&end={}&key={}'.format(closest_station,
                                                                                                      str(yesterday_date).split()[0],
                                                                                                      str(yesterday_date).split()[0],
                                                                                                      WEATHER_API_KEY
                                                                                                     ))
            #exit loop if current station already has data for current day
            if weather_data.json()['data'] and (weather_data.json()['data'][-1]['date'] == str(yesterday_date).split()[0]):
                break
        weather_data_entry = weather_data.json()['data'][0]
        #--------------------------------------------------
        #end get weather data
        
        
        #start get public holiday data
        #-------------------------------------------------
        province_public_holidays = []
        geolocator = Nominatim(user_agent="everyonecounts")
        location = geolocator.reverse(str(row['lat']) + "," + str(row['lon']))
        #when city=province, state is not returned
        if 'state' in location.raw['address']:
            province = location.raw['address']['state']
        else:
            province = location.raw['address']['city']
        province_abb = province_abbs[province]
        for date in holidays.DE(years=[yesterday_date.year], prov=province_abb):
            province_public_holidays.append(str(date))
        #end get public holiday data
        #-------------------------------------------------
        
        data_set={}   
        data_set['date']= str(yesterday_date).split()[0]
        data_set['bike_count']= str(bike_count_data_entry[1])
        data_set['name']= row['nom']
        data_set['lon']=row['lon']
        data_set['lat']=row['lat']
        data_set['temperature']= weather_data_entry['temperature']
        data_set['precipitation']= weather_data_entry['precipitation']
        data_set['snowdepth']= weather_data_entry['snowdepth']
        data_set['windspeed']= weather_data_entry['windspeed']
        data_set['sunshine']= weather_data_entry['sunshine']
        data_set['is_holiday']= 1 if str(yesterday_date).split()[0] in province_public_holidays else 0
        
        
        #start get prediction for normal bike count
        #-------------------------------------------------
        prediction = BP.predict_single(
            station_string=row['nom'],
            day=yesterday_date,
            temperature=data_set['temperature'] or 0,
            precipitation=data_set['precipitation'] or 0,
            snowdepth=data_set['snowdepth'] or 0,
            windspeed=data_set['windspeed'] or 0,
            sunshine=data_set['sunshine'] or 0,
            is_holiday=data_set['is_holiday'] or 0
        )
        #end get prediction for normal bike count
        #-------------------------------------------------
        #predict 0 if prediction -ve
        data_set['prediction'] = max(prediction,0)
        data_sets.append(data_set)
    return data_sets


# In[52]:


data = create_request()


# In[53]:


df = pd.DataFrame(data=data)


# In[55]:


df1 = df.fillna(0)


# In[56]:


data_json = df1.to_json(orient='records')


# In[48]:


client = boto3.client('s3')


# In[57]:


response = client.put_object(
  Bucket='sdd-s3-basebucket',
  Body=json.dumps(data_json),     
  Key='fahrrad/{}/{}.json'.format(yesterday_date.strftime('%Y/%m/%d'),str(yesterday_date).split()[0])
)
    


# In[ ]:




