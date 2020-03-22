import boto3
import json
import time
from datetime import date
import pandas as pd


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

#print(data)
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
result.to_csv("test.csv")
