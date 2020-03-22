## Required enviroment variables:

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- HYSTREET_TOKEN

## Run

- First run main.py. The script will create an data.csv file.
- Then run upload.py to upload the data to s3.

## Data Sample of one Day

```json
[
    {
        "timestamp": "2020-03-20T00:00:00.000+01:00",
        "station_id": 251,
        "pedestrians_count": 8,
        "unverified": false,
        "weather_condition": "rain",
        "temperature": 18.56,
        "min_temperature": 3.91,
        "date": "2020-03-20"
    {
        "timestamp": "2020-03-20T00:00:00.000+01:00",
        "station_id": 209,
        "pedestrians_count": 2,
        "unverified": false,
        "weather_condition": "partly-cloudy-day",
        "temperature": 8.91,
        "min_temperature": 4.09,
        "date": "2020-03-20"
    },
    ...
]
```
