from webbrowser import get

import boto3
import json
import time
from datetime import date
import pandas as pd
import pymongo
import csv

s3_client = boto3.client('s3')
date = date.today()
data = pd.DataFrame()
clientFirehose = boto3.client('firehose')

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


def getPlzDictionary ():
    with open('google_places_popularity/zuordnung_plz_ort_landkreis.csv', newline='', encoding='utf-8') as csvfile:
        plz_dictionary = {}
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                plz=row[3]
                landkreis=row[2]
                #print("row:"+plz+" landkreis:"+landkreis)
                plz_dictionary[plz]=landkreis

    return plz_dictionary

def extract_ags_from_plz(row):
    #print(row["address"])
    plz_dictionary = getPlzDictionary()

    plz = row["address"].split(",")[-2].split(" ")
    for ele in plz:
        try:
            ags = plz_dictionary[ele]
            #print("found ags")
            return ags
        except:
            #print("error: cant find ags")
            return None

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
data["ags"] = data.apply(extract_ags_from_plz,axis = 1, result_type = "reduce" )
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
    data_index = json.dumps({
        'name': landkreis,
        # todo time from request
        'date': str(date),
         'gmap_score' : relative_popularity
         #"airquality_score" : airquality_score
         #'hystreet_score' : hystreet_score
         # 'cycle_score' : cycle_score
    })
    data_index2 = {
        'name': landkreis,
        "lon" : lon,
        "lat" : lat,
        # todo time from request
        'date': str(date),
         'gmap_score' : relative_popularity
         #"airquality_score" : airquality_score
         #'hystreet_score' : hystreet_score
         # 'cycle_score' : cycle_score
    }
    list_results.append(data_index2 )
    print (data_index)
    # clientFirehose.put_record(DeliveryStreamName='sdd-kinese-aggregator',  Record={'Data':data_index })


    print(input)

s3_client.put_object(Bucket='sdd-s3-basebucket', Key="aggdata/live", Body=json.dumps(list_results))


