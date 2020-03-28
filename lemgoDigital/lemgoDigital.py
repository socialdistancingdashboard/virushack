from datetime import datetime
import boto3
import requests
import json
import csv

def to_data(city_name, lat, lon, traffic_list, passerby_list, noise_list):

    return {
        'landkreis_name': city_name,
        'datetimeRequest': datetime.now().isoformat(),
        'lat': lat,
        'lon': lon,
        'data': {
            'trafficPerHour': traffic_list,
            'passerbyPerHour': passerby_list,
            'noiseInDb': noise_list,
        }
    }

def fetch_csv(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    csv_reader = csv.reader(response.text.strip().split('\r\n'),delimiter=";")
    return csv_reader

def traffic_csv_to_json(csv_reader):
    if csv_reader is None:
        return {}
    header = next(csv_reader)
    # Check file as empty
    result = {}
    if header is not None:
        # Iterate over each row after the header in the csv
        i = 0
        for row in csv_reader:
            print(row)
            result[i] = {}
            result[i]['timestamp'] = row[0]
            result[i]['trafficNormal'] = row[1]
            result[i]['trafficCurrent'] = row[2]
            i += 1
        return result
    return None

def passerby_csv_to_json(csv_reader):
    if csv_reader is None:
        return {}
    header = next(csv_reader)
    # Check file as empty
    result = {}
    if header is not None:
        # Iterate over each row after the header in the csv
        i = 0
        for row in csv_reader:
            print(row)
            result[i] = {}
            result[i]['timestamp'] = row[0]
            result[i]['passerbyNormal'] = row[1]
            result[i]['passerbyCurrent'] = row[2]
            i += 1
        return result
    return None

def noise_csv_to_json(csv_reader):
    if csv_reader is None:
        return {}
    header = next(csv_reader)
    # Check file as empty
    result = {}
    if header is not None:
        # Iterate over each row after the header in the csv
        i = 0
        for row in csv_reader:
            print(row)
            result[i] = {}
            result[i]['timestamp'] = [row[0]]
            result[i]['noise_level'] = [row[1]]
            i += 1
        return result
    return None


traffic_list = traffic_csv_to_json(fetch_csv("https://dashboard.lemgo-digital.de/nodered/traffic"))
passerby_list = passerby_csv_to_json(fetch_csv("https://dashboard.lemgo-digital.de/nodered/passerby"))
noise_list = noise_csv_to_json(fetch_csv("https://dashboard.lemgo-digital.de/nodered/noise"))

data_for_S3 = to_data(city_name='Lemgo', lat=52.0266732, lon=8.9018625, traffic_list=traffic_list,
                      passerby_list=passerby_list, noise_list=noise_list)

s3_client = boto3.client('s3')
date = datetime.now()

if len(data_for_S3) > 0:
    response = s3_client.put_object(Body=json.dumps(data_for_S3), Bucket='sdd-s3-basebucket',
                                    Key='lemgo-digital/{}/{}/{}/{}'.format(str(date.year).zfill(4),
                                                                           str(date.month).zfill(2),
                                                                           str(date.day).zfill(2),
                                                                           str(date.hour).zfill(2)))
    print("Response: " + str(response))
