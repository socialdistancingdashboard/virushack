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

for x in range(9,19):
    try:
        response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='googleplaces/{}/{}/{}/{}.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day-1).zfill(2), str(x).zfill(2)))
        result = pd.DataFrame(json.loads(response["Body"].read()))
        result["date"] = date
        result["hour"] = x
        data = data.append(result)
    except:
        pass

def normal_popularity(row):
    return row["populartimes"][row["date"].weekday()]["data"][row["hour"]]


def getPlzDictionary ():
    with open('zuordnung_plz_ort_landkreis.csv', newline='', encoding='utf-8') as csvfile:
        plz_dictionary = {}
        fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                plz=row[3]
                landkreis=row[2]
                plz_dictionary[plz]=landkreis

    return plz_dictionary


data["normal_popularity"] = data.apply(normal_popularity, axis = 1, result_type = "reduce")
data["relative_popularity"] = data["current_popularity"] / data["normal_popularity"]
data["coordinates"] = data["coordinates"].astype(str)
result = pd.DataFrame(data.groupby(["id", "address", "coordinates"])["relative_popularity"].mean())
result = result.reset_index()
def extract_plz(row):
    #print(row["address"])
    plz = row["address"].split(",")[-2].split(" ")[1]
    #print(plz)
    return plz
result["plz"] = result.apply(extract_plz, axis = 1, result_type = "reduce")
result = result.drop(columns=["address"])

plz_dictionary = getPlzDictionary()

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
client = pymongo.MongoClient('mongodb://sddmongodb1:sdd123456@sdd-amazon-docdb.cluster-chjfvfcgw69a.eu-central-1.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false')
##Specify the database to be used
db = client.sddGooglePlacesDB
##Specify the collection to be used
col = db.sddGooglePlacesColl

for index, row in result.iterrows():
    landkreis = plz_dictionary[row['plz']]
    relative_popularity = row['relative_popularity']
    input = {'date':date.isoformat(), 'landkreis':landkreis,'relative_popularity':relative_popularity}
    print(input)
#col.update()
#print(plz_dictionary)



##Insert a single document
#col.insert_one()

