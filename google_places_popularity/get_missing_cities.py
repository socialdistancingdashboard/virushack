import requests
import pandas as pd
import datetime
import json
import numpy as np
from coords_to_kreis import coords_convert

#Specify Timeframe
#min_date = datetime.datetime.now().date() - datetime.timedelta(days=6)
#max_date = datetime.datetime.now().date()
#params = {"min_date": str(min_date), "max_date": str(max_date)}
response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod')
response.json()
data = pd.DataFrame()
for day, data_day in response.json()["body"].items():
    # if day == "2020-03-23":
    #     continue
    daily_data = pd.DataFrame.from_dict(data_day, orient='index')
    daily_data = daily_data.reset_index()
    daily_data["date"] = day
    data = data.append(daily_data)

data.columns
# 'index': AGS-ID of Landkreis
# 'date': Date of measurement
# 'gmap_score': How many people are at transit stations compared to normal day?
# 'hystreet_score': How many people are walking by hystreet sensors compared to normal day?
# 'nationalExpress_score': 'national_score', 'regional_score','suburban_score', 'bus_score', 'zug_score': How many connections got cancelled?
# "bike_score": How many people were travelling on bikes that day compared to a normal day? Here someone used fancy machine learning to cancel out the effect of weather.
# 'webcam_score': How many people are visible on webcams in public places divided by 2.4 (->we dont have a "normal" value here so we use 1/highscore median)
data.loc[data["gmap_score"].notna()]["index"].unique()
data.replace(np.inf, np.nan, inplace=True)
ags = data.loc[data["gmap_score"].notna()]["index"].unique()

cities = pd.read_csv("de_cities.csv", sep = ",")
cities = cities.iloc[:,:3]
cities.columns = ["stadt", "lat", "lon"]
cities["ags"] = coords_convert(cities)
cities.shape
len(cities["ags"].unique())
cities = cities.drop_duplicates("ags")
cities.to_csv("de_cities_unique_ags.csv")
cities.shape
cities = cities.loc[~cities["ags"].isin(ags)]
cities.iloc[:,0:3]
cities.iloc[:,:3].to_csv("missing.csv")
