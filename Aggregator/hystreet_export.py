import boto3
import pandas as pd
import json
from datetime import datetime, timedelta
from datetime import date as dt
from coords_to_kreis import coords_convert
from tqdm import tqdm
import settings

result_df = pd.DataFrame()
for x in tqdm(range(700)):
    date = dt.today() - timedelta(days=x)
    s3_client = boto3.client('s3')
    data = pd.DataFrame()
    clientFirehose = boto3.client('firehose')

    try:
        response = s3_client.get_object(Bucket=settings.BUCKET, Key='hystreet/{}/{}/{}'.format(
        str(date.year).zfill(4), str(date.month).zfill(2), str(date.day-3).zfill(2)))
    except:
        continue
    result = pd.DataFrame(json.loads(response["Body"].read()))
    data = data.append(result)


    def compute_weekday(timestamp):
        date_str = timestamp.split('+')[0]
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
        return date.weekday()


    data['weekday'] = float("NaN")
    for index, row in data.iterrows():
        data.at[index, 'weekday'] = compute_weekday(row['timestamp'])

    station_means = pd.read_csv('station_means.csv')

    data = pd.merge(data, station_means, left_on=['station_id', 'weekday'],
                    right_on=['station_id_mean', 'weekday_mean'], how='left').drop(['station_id_mean', 'weekday_mean'], axis=1)

    data['relative_pedestrians_count'] = float("NaN")
    for index, row in data.iterrows():
        data.at[index, 'relative_pedestrians_count'] = row['pedestrians_count'] / \
            row['mean_pedestrians_count_weekday']


    stations_with_ags = pd.read_csv('data/stations_with_ags.csv')
    data_with_ags = pd.merge(data, stations_with_ags, left_on='station_id',
                             right_on='stationid', how='left').drop('stationid', axis=1)
    data_with_ags['landkreis'] = coords_convert(data_with_ags)
    result_df = result_df.append(data_with_ags, sort = True)

result_df.columns

def compute_weekday(timestamp):
    date_str = timestamp.split('+')[0]
    date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
    return date.weekday()


result_df["city"].unique()
result_df = result_df.loc[(result_df["pedestrians_count"] > 0)]
result_df["weekday"] = result_df["timestamp"].apply(compute_weekday)
temp = pd.DataFrame(result_df.groupby(["station_id", "weekday"])["pedestrians_count"].mean())
temp = temp.reset_index()
temp.columns = ["station_id_mean","weekday_mean","mean_pedestrians_count_weekday"]
temp.to_csv("station_means.csv")

temp = result_df.loc[(result_df["city"] == "Berlin") & result_df["pedestrians_count"].notna() & (result_df["pedestrians_count"] > 0)]
temp.loc[temp["pedestrians_count"] > 0]["station_id"].value_counts()
temp.loc[temp["station_id"] == 94].plot("date", "pedestrians_count")
temp = temp["date"].value_counts()
temp.sort_index().to_csv("hystreet_export.csv")
