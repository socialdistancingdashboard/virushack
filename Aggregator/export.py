import requests
import pandas as pd
import datetime
import json
import numpy as np

#Specify Timeframe
min_date = datetime.datetime.now().date() - datetime.timedelta(days=6)
max_date = datetime.datetime.now().date()
params = {"min_date": str(min_date), "max_date": str(max_date), "data_sources":"0,1,2"}
response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod',params = params)
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

data.replace(np.inf, np.nan, inplace=True)
data.loc[data["hystreet_score"].notna()]["date"].unique()
aggregate = data.groupby("date")[['bike_score', 'bus_score', 'gmap_score', 'hystreet_score', 'nationalExpress_score', 'national_score', 'regional_score','suburban_score', 'webcam_score', 'zug_score']].mean()
pd.DataFrame(aggregate).to_csv("aggregate.csv")


data.to_csv("export.csv")
