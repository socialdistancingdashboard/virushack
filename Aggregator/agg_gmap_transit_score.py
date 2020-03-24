from webbrowser import get
from coords_to_kreis import coords_convert
import boto3
import json
import time
from datetime import date
import pandas as pd
import pymongo
import csv


def aggregate(date):
    s3_client = boto3.client('s3')

    data = pd.DataFrame()
    #clientFirehose = boto3.client('firehose')

    for x in range(9,19):
        try:
            response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='googleplaces/{}/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(x).zfill(2)))
            result = pd.DataFrame(json.loads(response["Body"].read()))
            result["date"] = date
            result["hour"] = x
            data = data.append(result)
        except:
            pass

    def normal_popularity(row):
        return row["populartimes"][row["date"].weekday()]["data"][row["hour"]]

    def to_data(landkreis, date, relative_popularity, airquality_score,hystreet_score,cycle_score):

        #['id', 'name', 'date', 'gmap_score', 'hystreet_score', 'cycle_score']
         return {
            'name': landkreis,
            # todo time from request
            'date': date,
            'gmap_score' : relative_popularity
             #"airquality_score" : airquality_score
             #'hystreet_score' : hystreet_score
             # 'cycle_score' : cycle_score
        }


    import ast
    data["normal_popularity"] = data.apply(normal_popularity, axis = 1, result_type = "reduce")
    data["relative_popularity"] = data["current_popularity"] / data["normal_popularity"]
    data["coordinates"] = data["coordinates"].astype(str)
    lat = []
    lon = []
    for index, row in data.iterrows():
        lat.append(ast.literal_eval(row["coordinates"])["lat"])
        lon.append(ast.literal_eval(row["coordinates"])["lng"])

    data["lat"] = lat
    data["lon"] = lon
    #print(data)
    data["ags"] = coords_convert(data)
    data2 = data.loc[data["ags"].notna()]


    result = pd.DataFrame(data2.groupby("ags")[["relative_popularity","lat", "lon"]].mean())

    result = result.reset_index()
    list_results = []
    for index, row in result.iterrows():
        landkreis = row['ags']
        relative_popularity = row['relative_popularity']
        try:
            lat = row["lat"]
            lon = row["lon"]
        except:
            lat = None
            lon = None#
            continue
        data_index = {
            "landkreis": landkreis,
            # todo time from request
            #'date': str(date),
            'gmap_score' : relative_popularity
             #"airquality_score" : airquality_score
             #'hystreet_score' : hystreet_score
             # 'cycle_score' : cycle_score
        }
        data_index2 = {
            'landkreis': landkreis,
            "lon" : lon,
            "lat" : lat,
            # todo time from request
            'date': str(date),
            'gmap_transit_score' : relative_popularity
             #"airquality_score" : airquality_score
             #'hystreet_score' : hystreet_score
             # 'cycle_score' : cycle_score
        }
        list_results.append(data_index)
        #print (data_index)
        # clientFirehose.put_record(DeliveryStreamName='sdd-kinese-aggregator',  Record={'Data':data_index })


        #print(input)
    return list_results

#aggregate()
