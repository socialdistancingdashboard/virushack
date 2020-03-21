# airquality data

## Idea
Our assumption is that air quality correlates with social distancing, e.g. less CO2 emissions if fewer people drive around in cars or trucks, or businesses/factories go on shutdowns.

## Data
Currently we only fetch data from https://aqicn.org/

See example here: https://aqicn.org/city/beijing/

You can find their API docs here: https://aqicn.org/json-api/doc/#api-Geolocalized_Feed-GetGeolocFeed

We assume the AQI (Real-time Air Quality Index ) is a good overall index for the purpose of this hackathon

An example for Berlin: https://aqicn.org/city/germany/berlin/
### In scope
- fetching data for all "Landkreise", see kreise_mit_center.csv for more info

### Out of scope
- fetching historical data
- fetching forecasts
- in depth analysis of data points

### Open Questions
- understand what AQI means, e.g. good, moderate, bad values (rule of thumb, the lower the better)

### Persisted Record
Please not that this is just an example and data might not be consistent
```
{
  'landkreis_name': 'Südwestpfalz',
  'datetime': '2020-03-21 18:15:09.328316',
  'lat': '49.20807801390453',
  'lon': '7.65775790003346',
  'airquality': {
    'aqi': 2,
    'iaqi': {
      'dew': {
        'v': 3
      },
      'h': {
        'v': 95.3
      },
      'no2': {
        'v': 9.6
      },
      'o3': {
        'v': 17.9
      },
      'p': {
        'v': 1022.5
      },
      'pm10': {
        'v': 2
      },
      't': {
        'v': 3.6
      },
      'w': {
        'v': 8.2
      },
      'wg': {
        'v': 11.3
      }
    }
  }
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

## MISC Dev template
### AWS and firehose
We used ``boto3`` as client to connect to ``firehose``
```
client = boto3.client('firehose')
...
client.put_record(DeliveryStreamName='sdd-kinesis-<your data bucket>',
                  Record={'Data': base64.b64encode(<your data string>)})
```

Check with @Tho to get your ``DeliveryStreamName``