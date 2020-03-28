import json
from datetime import date, timedelta
import boto3
import pandas as pd

date = date.today()


def path_to_hour_of_day(path: str):
    strValue = path.split('/')[-1]
    return strValue


def get_relative_traffic(object_body_json):
    traffic_per_hour_object = object_body_json['data']['trafficPerHour']
    traffic_per_hour_dp = json.dumps(traffic_per_hour_object)
    traffic_per_hour_dp = pd.DataFrame(json.loads(traffic_per_hour_dp)).transpose()
    traffic_per_hour_dp['relativTraffic'] = pd.to_numeric(traffic_per_hour_dp['trafficNormal']) / pd.to_numeric(
        traffic_per_hour_dp['trafficCurrent'])
    return traffic_per_hour_dp


def get_relative_passerby(object_body_json):
    passerby_per_hour_object = object_body_json['data']['passerbyPerHour']
    passerby_per_hour_dp = json.dumps(passerby_per_hour_object)
    passerby_per_hour_dp = pd.DataFrame(json.loads(passerby_per_hour_dp)).transpose()
    passerby_per_hour_dp['relativPasserby'] = pd.to_numeric(passerby_per_hour_dp['passerbyCurrent']) / pd.to_numeric(
        passerby_per_hour_dp['passerbyNormal'])
    return passerby_per_hour_dp


def aggregate(date):
    s3_client = boto3.client('s3')

    s3_objects = s3_client.list_objects_v2(Bucket='sdd-s3-basebucket',
                                           Prefix='lemgo-digital/{}/{}/{}/'.format(str(date.year).zfill(4),
                                                                                   str(date.month).zfill(2),
                                                                                   str(date.day).zfill(2)))
    if 'Contents' not in s3_objects:
        return []

    print("Found " + str(len(s3_objects['Contents'])) + " elements")
    dict_s3_objects = {}
    for key in s3_objects['Contents']:
        dict_s3_objects[path_to_hour_of_day(key['Key'])] = s3_client.get_object(Bucket='sdd-s3-basebucket',
                                                                                Key=key['Key'])

    latest_lemgo_digital_object = dict_s3_objects[sorted(dict_s3_objects.keys(), reverse=False)[0]]
    object_body = str(latest_lemgo_digital_object["Body"].read(), 'utf-8')

    object_body_json = json.loads(object_body)
    traffic_per_hour_dp = get_relative_traffic(object_body_json)
    passerby_per_hour_dp = get_relative_passerby(object_body_json)

    traffic_per_hour_dp.set_index("timestamp")
    passerby_per_hour_dp.set_index("timestamp")
    aggregated_value = pd.merge(traffic_per_hour_dp, passerby_per_hour_dp, how='left', left_on='timestamp',
                                right_on='timestamp')

    aggregated_value.reset_index()
    aggregated_value['lemgoDigitalAggregated'] = 0.3 * aggregated_value['relativTraffic'] + 0.7 * aggregated_value[
        'relativPasserby']

    list_results = []
    date_minus_one = date - timedelta(days=1)
    # aggregated_value_for_day = aggregated_value.loc[aggregated_value['timestamp'] == str(date_minus_one)]
    data_index = {
        'landkreis': 'Lemgo',
        'timestamp': aggregated_value['timestamp'],
        'lemgoDigitalAggregated': aggregated_value['lemgoDigitalAggregated']
    }
    list_results.append(data_index)

    return list_results
