# airquality data

## Idea
Our assumption is that air quality correlates with social distancing, e.g. less CO2 emissions if fewer people drive around in cars or trucks, or businesses/factories go on shutdowns.

## Data
Currently we only fetch data from https://aqicn.org/

See example here: https://aqicn.org/city/beijing/

You can find their API docs here: https://aqicn.org/json-api/doc/#api-Geolocalized_Feed-GetGeolocFeed

We assume the AQI (Real-time Air Quality Index ) is a good overall index for the purpose of this hackathon

### In scope
- fetching data for all "Landkreise", see kreise_mit_center.csv for more info

### Out of scope
- fetching historical data
- fetching forecasts
- in depth analysis of data points

### Open Questions
- understand what AQI means, e.g. good, moderate, bad values

### Firehose Record
Please not that this is just an example and data might not be consistent
```
{
    'landkreis_name': 'Südwestpfalz',
    'datetime': '2020-03-21 18:15:09.328316',
    'lat': 7.65775790003346,
    'lon': 49.20807801390453,
    'airquality': '{
                       "status": "ok",
                       "data": {
                           "aqi": 147,
                           "idx": 1437,
                           "attributions": [
                               {
                                   "url": "https://china.usembassy-china.org.cn/embassy-consulates/shanghai/air-quality-monitor-stateair/",
                                   "name": "U.S. Consulate Shanghai Air Quality Monitor"
                               },
                               {
                                   "url": "https://sthj.sh.gov.cn/",
                                   "name": "Shanghai Environment Monitoring Center(上海市环境监测中心)"
                               },
                               {
                                   "url": "http://106.37.208.233:20035/emcpublish/",
                                   "name": "China National Urban air quality real-time publishing platform (全国城市空气质量实时发布平台)"
                               },
                               {
                                   "url": "https://waqi.info/",
                                   "name": "World Air Quality Index Project"
                               }
                           ],
                           "city": {
                               "geo": [
                                   31.2047372,
                                   121.4489017
                               ],
                               "name": "Shanghai (上海)",
                               "url": "https://aqicn.org/city/shanghai"
                           },
                           "dominentpol": "pm25",
                           "iaqi": {
                               "co": {
                                   "v": 8.2
                               },
                               "h": {
                                   "v": 93
                               },
                               "no2": {
                                   "v": 23.4
                               },
                               "o3": {
                                   "v": 33.3
                               },
                               "p": {
                                   "v": 1007.4
                               },
                               "pm10": {
                                   "v": 52
                               },
                               "pm25": {
                                   "v": 147
                               },
                               "so2": {
                                   "v": 2.1
                               },
                               "t": {
                                   "v": 17.7
                               },
                               "w": {
                                   "v": 0.2
                               }
                           },
                           "time": {
                               "s": "2020-03-21 23:00:00",
                               "tz": "+08:00",
                               "v": 1584831600
                           },
                           "debug": {
                               "sync": "2020-03-22T01:28:00+09:00"
                           }
                       }
                   }'
}
```

## How to contribute
### Request API token
Request an API here https://aqicn.org/data-platform/token/#/

### Request AWS credentials and confi
Please ask @Tho for aws credentials to access AWS firehose, unzip and move to /Users/<you>/.aws
export AIR_QUALITY_API_TOKEN=<your token>

### Run
```python airquality/airquality.py```