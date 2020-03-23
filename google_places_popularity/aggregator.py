from webbrowser import get

import boto3
import json
import time
from datetime import date
import pandas as pd
import pymongo
import csv
import ast
import base64


def getAirquality():
    result = pd.DataFrame()
    list = []
    s3_objects = s3_client.list_objects_v2(Bucket='sdd-s3-basebucket',
                                           Prefix='airquality/{}/{}/{}/'.format(str(date.year).zfill(4),
                                                                                str(date.month).zfill(2),
                                                                                str(date.day).zfill(2)))

    if 'Contents' not in s3_objects:
        return []
    file_list = []
    print("Found " + str(len(s3_objects['Contents'])) + " elements")
    for key in s3_objects['Contents']:
        airqualityObject = s3_client.get_object(Bucket='sdd-s3-basebucket', Key=key['Key'])
        object_body = str(airqualityObject["Body"].read(), 'utf-8')

        print(object_body)
        airquality_json = pd.json_normalize(json.loads(object_body))
        # except:
        #  pass

        # result.append(pd.json_normalize(airquality_json))
        # x=pd.DataFrame(airquality_json)
        # result.append(x)
        list.append(pd.DataFrame(airquality_json))

    merged = pd.concat(list)
    # merged = merged.to_frame()
    print(merged)

    # merged=data.apply(aqi, axis=1, result_type="reduce")
    print(merged)
    # result = pd.DataFrame(data2.groupby("ags")[["relative_popularity", "lat", "lon"]].mean())
    result = pd.DataFrame(merged.groupby("landkreis_name")[["lat", "lon"]].mean())

    print(result)
    x = result[result.landkreis_name.eq('Berlin')]
    print(result[result['landkreis_name'] == "Berlin"].shape)
    print(result[result.Letters == 'Berlin'].Letters.item)
    print(result)
    # p=pd.concat(result)
    print(p)

    result = result.reset_index()

    return result
    # result = pd.DataFrame(json.loads(obj))

    # objects = s3_client.list_objects(Bucket='sdd-s3-basebucket/airquality/{}/{}/{}/'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
    # data = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='airquality/{}/{}/{}/'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2) ))

    # result = pd.DataFrame(json.loads(response["Body"].read()))
    # except:
    #   pass


def normal_popularity(row):
    return row["populartimes"][row["date"].weekday()]["data"][row["hour"]]


def aqi(row):
    return row["airquality"]


def get_plz_to_ags_dictionary():
    with open('zuordnung_plz_ort_landkreis.csv', newline='', encoding='utf-8') as csvfile:
        plz_dictionary = {}
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                plz = row[3]
                landkreis = row[2]
                # print("row:"+plz+" landkreis:"+landkreis)
                plz_dictionary[plz] = landkreis

    return plz_dictionary


def extract_ags_from_plz(row, dict_plz_ags):
    # print(row["address"])

    plz = row["address"].split(",")[-2].split(" ")
    for ele in plz:
        try:
            ags = dict_plz_ags[ele]
            # print("found ags")
            return ags
        except:
            # print("error: cant find ags")
            return None


def to_data(landkreis, date, relative_popularity, airquality_score, hystreet_score, cycle_score):
    # ['id', 'name', 'date', 'gmap_score', 'hystreet_score', 'cycle_score']
    return {
        'name': landkreis,
        # todo time from request
        'date': date,
        'gmap_score': relative_popularity
        # "airquality_score" : airquality_score
        # 'hystreet_score' : hystreet_score
        # 'cycle_score' : cycle_score
    }


def getGoogleData():
    data = pd.DataFrame()
    for x in range(9, 19):
        try:
            response = s3_client.get_object(Bucket='sdd-s3-basebucket',
                                            Key='googleplaces/{}/{}/{}/{}'.format(str(date.year).zfill(4),
                                                                                  str(date.month).zfill(2),
                                                                                  str(date.day).zfill(2),
                                                                                  str(x).zfill(2)))
            result = pd.DataFrame(json.loads(response["Body"].read()))
            result["date"] = date
            result["hour"] = x
            data = data.append(result)
        except:
            pass

    data["normal_popularity"] = data.apply(normal_popularity, axis=1, result_type="reduce")
    data["relative_popularity"] = data["current_popularity"] / data["normal_popularity"]
    data["coordinates"] = data["coordinates"].astype(str)
    lat = []
    lon = []
    for index, row in data.iterrows():
        lat.append(ast.literal_eval(row["coordinates"])["lat"])
        lon.append(ast.literal_eval(row["coordinates"])["lng"])

    data["lat"] = lat
    data["lon"] = lon
    data["ags"] = data.apply(extract_ags_from_plz(row, dict_plz_ags), axis=1, result_type="reduce")
    data2 = data.loc[data["ags"].notna()]

    result = pd.DataFrame(data2.groupby("ags")[["relative_popularity", "lat", "lon"]].mean())

    result = result.reset_index()
    return result


s3_client = boto3.client('s3')
date = date.today()
data = pd.DataFrame()
clientFirehose = boto3.client('firehose')
dict_plz_ags = get_plz_to_ags_dictionary()

# data_google_data = getGoogleData();
data_airquality = getAirquality();

list_results = []
for index, row in data_airquality.iterrows():
    landkreis = row['ags']
    relative_popularity = row['relative_popularity']
    try:
        lat = row["lat"]
        lon = row["lon"]
    except:
        lat = None
        lon = None  #
        continue
    data_index = json.dumps({
        'name': landkreis,
        # todo time from request
        'date': str(date),
        'gmap_score': relative_popularity
        # "airquality_score" : airquality_score
        # 'hystreet_score' : hystreet_score
        # 'cycle_score' : cycle_score
    })
    data_index2 = {
        'name': landkreis,
        "lon": lon,
        "lat": lat,
        # todo time from request
        'date': str(date),
        'gmap_score': relative_popularity
        # "airquality_score" : airquality_score
        # 'hystreet_score' : hystreet_score
        # 'cycle_score' : cycle_score
    }
    list_results.append(data_index2)
    print(data_index)
    # clientFirehose.put_record(DeliveryStreamName='sdd-kinese-aggregator',  Record={'Data':data_index })

    print(input)

s3_client.put_object(Bucket='sdd-s3-basebucket', Key="aggdata/live", Body=json.dumps(list_results))
