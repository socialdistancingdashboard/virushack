import requests
import json
import pandas as pd
import csv
import populartimes
import time
from tqdm import tqdm

with open("api_keys.txt") as f:
        api_key = f.readline()

def get_all_places(lat,long, radius):
    page_ids = []
    params = {
        "location": str(lat) + "," + str(long),
        "radius": radius,
        "type": "transit_station",
        "key": api_key
    }
    for x in range(3):
        #print(x)
        r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", params = params)
        #print(r.url)
        data = r.json()
        #print(data)
        #print(len(data["results"]))
        page_ids = page_ids + [result["place_id"] for result in data["results"]]
        if "next_page_token" in data:
            time.sleep(5)
            #print("fetching page " + str(x+1))
            next_page = data["next_page_token"]
            params = {
                "key": api_key,
                "pagetoken": next_page
            }
        else:
            break
    return page_ids

def filter_popularity_available(place_ids):

    result = []
    #print(len(place_ids))
    for x, place_id in enumerate(tqdm(place_ids)):
        try:
            data = populartimes.get_id(api_key, place_id)
        except Exception as e:
            print(e)
            print("Error with " + str(place_id))
            continue
        #print(data)
        if "current_popularity" in data:
            #print("found")
            result.append(place_id)
    return result

def read_data_csv(file, encoding = "UTF-8", sep = ","):
    places = pd.read_csv(file, encoding = encoding, sep = sep, names = ["city", "lat", "long"], header = 0)
    #print(places.head())
    #print(places.shape)
    with open("place_ids/missing_ids.csv") as f:
         id_list = [key.strip() for key in f.readlines()]
    #id_list = []
    for index , row in tqdm(places[65:].iterrows()):
        print(row[0])
        time.sleep(5)
        id_list = id_list + filter_popularity_available(get_all_places(row[1],row[2], 2000))
        print(len(id_list))
        pd.DataFrame(id_list).to_csv("place_ids/" + str(file.split(".")[0]) + "_ids.csv", index=False, header=False)

#"Weißenburg"

read_data_csv("missing.csv")
#populartimes.get_id(api_key, "ChIJnc3vbEgJvUcRxGJfy-eGHW8")
