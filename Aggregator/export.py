import requests
import pandas as pd
import datetime
import json
import numpy as np

#Specify Timeframe
min_date = datetime.datetime.now().date() - datetime.timedelta(days=3)
max_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
params = {"min_date": str(min_date), "max_date": str(max_date)}
params
response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod',params = params)
response.json()["body"]

for day, data_day in response.json()["body"].items():
    if day == "2020-03-23":
        continue
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

data.replace(np.inf, np.nan, inplace=True)
1/data["hystreet_score"].median()
data.loc[data["date"] == "2020-03-22"]["hystreet_score"].corr(data.loc[data["date"] == "2020-03-22"]["gmap_score"])

data.loc[data["date"] == "2020-03-22"].plot("hystreet_score", "gmap_score", kind ="scatter")
data.to_csv("export.csv")
