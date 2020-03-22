import pandas as pd
from datetime import datetime, date


def compute_weekday(timestamp):
    date_str = timestamp.split('+')[0]
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
    return date.weekday()


data = pd.read_csv('data.temp.csv')

data['weekday'] = float("NaN")
for index, row in data.iterrows():
    data.at[index, 'weekday'] = compute_weekday(row['timestamp'])

# compute mean pedestrians for stations by weekday
station_means = data.groupby(['station_id', 'weekday']).mean().reset_index().rename(columns={'pedestrians_count': 'mean_pedestrians_count_weekday', 'station_id': 'station_id_mean', 'weekday': 'weekday_mean'})[
    ['station_id_mean', 'weekday_mean', 'mean_pedestrians_count_weekday']]
station_means.to_csv('station_means.csv')
