API used Docu: https://api.meteostat.net
Get closest X weather stations using:
https://api.meteostat.net/v1/stations/nearby?lat=49&lon=9&limit=20&key={}
In example above closest 20 stations are fetched
Using station_id from closest station fetch historical weather data using:
https://api.meteostat.net/v1/history/daily?station=D4160&start=2019-08-02&end=2020-03-24&key={}
