import requests
import boto3
import pandas as pd
from unidecode import unidecode
import time
from tqdm import tqdm
import json

s3_client = boto3.client('s3')

cities = pd.read_csv("staedte_koordinaten_ueber_50k.CSV", sep = ";")
cities
errors = []
result = pd.DataFrame()
for x, row in tqdm(cities.iterrows()[:50], total=50):
    time.sleep(1)
    #print(row)
    try:
        r = requests.get("https://api.midway.tomtom.com/ranking/live/DEU%2FCircle%2F" + unidecode(row["Stadt"]).lower().replace(" ", "-"))
        data = pd.DataFrame(r.json()["data"])
        data["city"] = row["Stadt"]
        data["lat"] = row["Lat"]
        data["lon"] = row["Long"]
        result = result.append(data)
    except Exception as e:
        errors.append(row["Stadt"])
        print(row["Stadt"])
        print(e)

result["date"] = pd.to_datetime(result["UpdateTime"]*10**6).dt.date

pd.DataFrame(errors).to_csv("errors.csv")

for date, group in result.groupby("date"):
    group = group.reset_index()
    group["date"] = group["date"].astype(str)
    s3_client.put_object(Body=json.dumps(group.to_dict()),  Bucket='sdd-s3-basebucket',
              Key='tomtom/{}/{}/{}.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)))
