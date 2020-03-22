import requests
import pandas as pd
import os
import json
import datetime

df = pd.DataFrame(columns=['timestamp', 'station_id', 'pedestrians_count',
                           'unverified', 'weather_condition', 'temperature', 'min_temperature'])

headers = {'Content-Type': 'application/json',
           'X-API-Token': os.getenv('HYSTREET_TOKEN')}
res = requests.get('https://hystreet.com/api/locations/', headers=headers)
locations = res.json()
for location in locations:
    res = requests.get('https://hystreet.com/api/locations/' +
                       str(location['id'])+'?resolution=day', headers=headers)
    location_detail = res.json()
    earliest_measurement_at = location_detail['metadata']['earliest_measurement_at'].split('T')[
        0]
    res = requests.get('https://hystreet.com/api/locations/' +
                       str(location['id'])+'?resolution=day&from='+earliest_measurement_at+'&to=2020-03-20', headers=headers)
    measurements = res.json()['measurements']
    for measurement in measurements:
        measurement['station_id'] = location_detail['id']

        date_str = measurement['timestamp'].split('+')[0]
        date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')

        measurement['date'] = date.strftime("%Y-%m-%d")
        df = df.append(measurement, ignore_index=True)
    print(json.dumps(measurements[0], indent=4))
df.to_csv('data.temp.csv', index=False)
