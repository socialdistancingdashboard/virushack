# ACHTUNG: livepad ist immer aktueller: https://hackmd.okfn.de/ujyaOP2UScWe2isgUe9pYA?both#

# Database und (GET) API Spezifikation

[TOC]
# Server
* AWS
* mysql db auf AWS
* lambdas exposen API
* Weitere Anforderungen:
    * Tensorflow
    * Cronjobs

# Datenbank "sdd" (social distancing dashboard)
## Tabelle holidays
### Quelle: (todo: Quelle angeben)
```sql
/* contains information about public holidays per state */
DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (
  id INT UNSIGNED auto_increment PRIMARY KEY,
  state_id VARCHAR(3) NOT NULL,
  dt DATETIME NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(state_id),
  INDEX(dt),
  UNIQUE(state_id, dt)
) CHARACTER SET utf8;
```

## Tabelle weather
### Quelle: (todo: Quelle angeben)
```sql
/* contains weather information since 2007-01-01 */
DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
  id INT UNSIGNED auto_increment PRIMARY KEY,
  temp DOUBLE NULL,
  temp_min DOUBLE NULL,
  temp_max DOUBLE NULL,
  rainfall DOUBLE NULL,
  snowfall DOUBLE NULL,
  snowdepth DOUBLE NULL,
  winddirection DOUBLE NULL,
  windspeed DOUBLE NULL,
  peakgust DOUBLE NULL,
  sunshine DOUBLE NULL,
  pressure DOUBLE NULL,
  district_id VARCHAR(32) NOT NULL,
  dt DATETIME NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(district_id),
  INDEX(dt)
) CHARACTER SET utf8;
```

API used Docu: https://api.meteostat.net
Get closest X weather stations using: 
https://api.meteostat.net/v1/stations/nearby?lat=49&lon=9&limit=20&key=PZKj8EOb
In example above closest 20 stations are fetched
Using station_id from closest station fetch historical weather data using:
https://api.meteostat.net/v1/history/daily?station=D4160&start=2019-08-02&end=2020-03-24&key=PZKj8EOb

## Tabelle locations

```sql
/* Contains meta information for all amtliche Gemeindeschlüssel */
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
  district_id VARCHAR(5) PRIMARY KEY, /* disttrict_id (=Landkreise in DL) */
  district VARCHAR(128) NOT NULL,
  district_type VARCHAR(128) NOT NULL,
  state_id VARCHAR(32) NOT NULL, /* "BW" "B" etc */
  state VARCHAR(128) NOT NULL, /* "Baden-Württemberg" */
  country_id VARCHAR(32) NOT NULL, /* "DE" */
  country VARCHAR(128) NOT NULL, /* "Deutschland" */
  lat DOUBLE NOT NULL,
  lon DOUBLE NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8;
```

## Tabelle categories

```sql
/* Contains the available score names */
DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
  name VARCHAR(64) PRIMARY KEY,
  desc_short TEXT NOT NULL,
  desc_long TEXT NOT NULL,
  contributors TEXT NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8;

```
## Tabelle scores_meta

```sql
DROP TABLE IF EXISTS scores_meta;
CREATE TABLE scores_meta (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  district_id VARCHAR(32) NOT NULL, /* regional identifier */
  category VARCHAR(64) NOT NULL, /* which source */
  meta TEXT NULL, /* stringified JSON dump with additional characteristics */
  description TEXT NULL, /* BHF Name, Webcam Standort, etc */
  source_id VARCHAR(128), /* Dient dazu innerhalb eines districts (Landkreis in DL) Quellen zu unterscheiden. Bspw. "Webcam Marktplatz" */
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(category),
  INDEX(district_id),
  UNIQUE(district_id, category, source_id) /* Meta Daten sind zeitunabhängig */
) CHARACTER SET utf8;

```
## Tabelle scores
```sql
/* Contains the actual data */
DROP TABLE IF EXISTS scores;
CREATE TABLE  scores (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
  dt DATETIME NOT NULL,
  score_value DOUBLE NOT NULL, /* social distancing measure */
  reference_value DOUBLE NULL DEFAULT 0, /* expected value without corona. */
  category VARCHAR(64) NOT NULL,
  district_id VARCHAR(32) NOT NULL, /* regional identifier (in DL Landkreis) */
  meta_id INT UNSIGNED NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source_id VARCHAR(128) NOT NULL, /* allows to distinguish multiple sources within one district */
  INDEX(category),
  INDEX(dt),
  INDEX(district_id)
) CHARACTER SET utf8;

```
## Tabelle measures
enthält politische Maßnahmen, die in einem Bezug zu Corona / social distancing stehen. Quelle: https://docs.google.com/spreadsheets/d/1KgiMHc3ZFoXbIxoEy1_sMF8wt3ElxpRwVOpH9xenbbM/edit#gid=0

```sql
DROP TABLE IF EXISTS measures;
CREATE TABLE measures (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY, /* no meaning */
  dt_announcement DATETIME NOT NULL, /* Datetime of publication */
  dt_start_action DATETIME NOT NULL, /* Datetime when action takes into effect */
  dt_end_action DATETIME NULL, /* Datetime when action is supposed to end */
  desc_short TEXT NOT NULL, /* Short description. */
  desc_long TEXT NOT NULL, /* Long description */
  level1_id_announced VARCHAR(32) NOT NULL, /* country code of place where measure was announced*/
  level2_id_announced VARCHAR(32) NOT NULL, /* county code of place where measure was announced*/
  level3_id_announced VARCHAR(32) NOT NULL, /* district code of place where measure was announced*/
  level1_id_action VARCHAR(32) NULL, /* country code if action is applicable */
  level2_id_action VARCHAR(32) NULL, /* county code if action is applicable */
  level3_id_action VARCHAR(32) NULL, /* district code if action is applicable */
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8;

```

# API
API Funktionen werden mithilfe von Lambdas nach außen exposed. Funktionalität wird im Folgendem spezifiziert.

## get_locations()
Holt alle verfügbaren Locations. (Derzeit 403 Landkreise plus Metainformationen).
* GET Endpoint (klicken zum ausprobieren)
  * https://ud89c9f90d.execute-api.eu-central-1.amazonaws.com/Prod/get-locations/
* returns 
```javascript
 [{
    "district_id": string, /* 5stellige Landkreis Id "01234567" */
    "district": string, /* "Kreis Karlsruhe" */
    "district_type": string, /* "Stadtkreis" */
    "state_id": string, /* "BW", "BY" */
    "state": string, /*  "Sachsen" */
    "country_id": string, /* "DE" */
    "country": string, /* "Deutschland" */
    "lat": double,
    "lon": double
  }]
```

## get_categories()
Holt alle verfügbaren Kategorien mit beschreibungen
* GET Endpoint (klicken zum ausprobieren)
  * https://cy7n0vv93c.execute-api.eu-central-1.amazonaws.com/Prod/get-categories/
* returns
```javascript
 [{
    "name": string,
    "desc_short": text,
    "desc_long": text
  }]
```

## get_spatial_data(opt)
Aggregiert für jeweils alle angefragten Kategorien sowohl
* zeitlich: die Daten im Zeitfensert start bis end, als auch
* räumlich: Für die gewählte spatial_granularity.

### Ausprobieren
* POST Request testen: https://reqbin.com/
  * URL: https://vc9x7cb4ka.execute-api.eu-central-1.amazonaws.com/Prod/get-spatial-data
  * Methode: POST
  * Wähle auf reqbin.com ->```json``` und füge die folgenden Parameter zum testen ein
  * Preconfigured test: https://reqbin.com/npnsnzgo

```javascript
{
  "start": "2020-03-01",
  "end": "2020-03-28",
  "categories": [
    "score_public_transportation_all",
    "score_public_transportation_bus"
  ],
  "spatial_granularity": 1
}
```
### Allgemeines Schema der Parameter bzw Filter

```javascript
opt = {
    "start": datetime, /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
    "end": datetime, /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
    "categories": string[], /* ["public_transportation_ice", "webcams"]*/
    "spatial_granularity": int /* 1: country, 2: state, 3: district*/
}
```
### Schema der Rückgabe
```javascript
res = {
    "request": {
        /*gespiegelte Request options, see above*/
    },
    "data": [
      "category": string,
      "desc_short": string, /* Kurzbeschreibung der Kategorie */
      "desc_long": string, /* Langbeschreibung der Kategorie */
      "values": [
        {
            "spatial_id": string /* "001234" OR "BW" OR "DE"*/
            "score": float /* 0.12 */
            "prediction": float /* derzeit auf null hard gecoded */
        }
      ]
    ]
}
```

## get_time_series(options)
Liefert Daten für die Darstellung als Zeitreihe. Aggregiert nicht zeitlich, nur räumlich entsprechend des spatial_levels (1: nation, 2: state, 3: district).

Funktion des Spatial Filters muss noch präzisiert werden
Jetzige Umsetzung ist nicht gemäß dieser Dokumentation

### Ausprobieren
  
* POST Request testen: https://reqbin.com/
  * URL: https://2q4vey3xeg.execute-api.eu-central-1.amazonaws.com/Prod/get-timeseries-data/
  * Methode: POST
  * Wähle auf reqbin.com ->```json``` und füge die folgenden Parameter zum testen ein
  * Preconfigured test:  https://reqbin.com/kh3yrsfx
### Testparameter
```javascript 
{
  "start": "2020-01-27",
  "end": "2020-01-30",
  "timeline_specs": [{
      "category": "score_public_transportation_all",
      "spatial_granularity": 2,
      "spatial_filters": ["BW"]
    },
    {
      "category": "score_public_transportation_all",
      "spatial_granularity": 2,
      "spatial_filters": ["BY"]
    }
  ]
}
```
### Allgemeines Parameter Schema
```javascript
opt = {
    "start": datetime, /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
    "end": datetime,  /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
    "timeline_specs": [{
      "category": string, /* ["public_transportation_ice", "webcams"]*/
      "spatial_granularity": int, /* 1: country, 2: state, 3: district*/
      "spatial_filters": string[] /* Leave empty for no filters, otherwise choose values such as "DE" for nation or "BW" for staté level or  "01234567" for districts */
      ]
    }]
}
```
### Schema der Rückgabe
```javascript
result = [
    {
       "request" = {
          "start": datetime /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
          "end": datetime /*[2020-03-22THH:MM:SS] ISO 6801 extended format*/
          "timeline_specs": [{
            "category": string, /* ["public_transportation_ice", "webcams"]*/
            "spatial_granularity": int, /* 1: country, 2: state, 3: district*/
            "spatial_filters": [ /* spatial_fitlers = [] if you want to get ALL data. */
              {"spatial_id": string} /* according to spatial level "DE" or "BW" or "01234567" */
            ]
          }]  
      },        
      "timelines": [ {
          "category": string,
          "description_short": string,
          "description_long": string,
          "spatial_granularity": int,
          "spatial_filters": ["spatial_id": string]
          "values": [
            {
                "datetime": datetime
                "score": number,
                "prediction": number /* derzeit auf null hard gecoded */
            }
         ]
      }]
    }
]
```
  
### get_locations(level, filter_level, filter_value)
Beispiel: Holt alle gemeindeschlüssel (level=3) für deutschland (filter_level=1, filter_value="de")
* returns json
```javascript
  [{
    "name": string (name für das gewählte level),
    "levelX_name": str
    "levelX_id": str
  }, ...]
  ```
  
## get_all() (noch nicht implementiert, die soll wissenschaftlern helfen alle daten roh aber strukturiert zu kopieren)
```javascript
opt = {
    "start_date": datetime /*[2020-03-22] */
    "end_date": datetime /*[2020-03-22]*/
    "categories": string[] /* ["public_transportation_ice", "webcams"]*/
}
```
Returns non-aggregated data
```javascript
result = [
    {
       "request" = {
            "start_date": datetime /*[2020-03-22]*/
            "end_date": datetime /*[2020-03-22]*/
            "categories": string[]
       },
        
       "categories": [
          "category": string,
          "description_short": string,
          "description_long": string,
          "values": [
            {
                "datetime": datetime
                "value_reference": number,
                "value_absolute": number,
                "value_score": number,
                "ags": string,
                "lon": double,
                "lat": double,
                "description": string,
                "meta": TEXT /* stringified JSON */             
            }
         ]
    }
]
```


# Examples

## Timeseries Example (get-timeseries-data)
* Preconfigured test: https://reqbin.com/kh3yrsfx
* URL: POST https://2q4vey3xeg.execute-api.eu-central-1.amazonaws.com/Prod/get-timeseries-data/

### Input
* POST https://2q4vey3xeg.execute-api.eu-central-1.amazonaws.com/Prod/get-timeseries-data/
```json
{
  "start": "2020-01-27",
  "end": "2020-01-30",
  "timeline_specs": [{
      "category": "score_public_transportation_all",
      "spatial_granularity": 2,
      "spatial_filters": ["BW"]
    },
    {
      "category": "score_public_transportation_all",
      "spatial_granularity": 2,
      "spatial_filters": ["BY"]
    }
  ]
}
```

### Output
```json
{
    "request": {
        "start": "2020-01-27T00:00:00",
        "end": "2020-01-28T00:00:00",
        "timeline_specs": [{
            "category": "score_public_transportation_all",
            "spatial_granularity": 2,
            "spatial_filters": ["BW"]
        }, {
            "category": "score_public_transportation_all",
            "spatial_granularity": 2,
            "spatial_filters": ["BY"]
        }]
    },
    "timelines": [{
        "category": "score_public_transportation_all",
        "description_short": "Beschreibt das Verh\u00e4ltnis aus tats\u00e4chlichen Haltestops und geplanten Haltestops f\u00fcr diverse \u00f6ffentliche Verkehrsmittel.",
        "description_long": "Die Daten sind ab 27.02.2020 f\u00fcr alle Gemeinden verf\u00fcgbar.",
        "spatial_granularity": 2,
        "spatial_filters": ["BW"],
        "values": [{
            "datetime": "2020-01-27T12:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T13:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T14:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T15:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T16:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T17:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T18:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T19:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T20:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T21:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T22:00:00Z",
            "score": 0.0110665468,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T23:00:00Z",
            "score": 0.0131184169,
            "prediction": 0
        }]
    }, {
        "category": "score_public_transportation_all",
        "description_short": "Beschreibt das Verh\u00e4ltnis aus tats\u00e4chlichen Haltestops und geplanten Haltestops f\u00fcr diverse \u00f6ffentliche Verkehrsmittel.",
        "description_long": "Die Daten sind ab 27.02.2020 f\u00fcr alle Gemeinden verf\u00fcgbar.",
        "spatial_granularity": 2,
        "spatial_filters": ["BY"],
        "values": [{
            "datetime": "2020-01-27T12:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T13:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T14:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T15:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T16:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T17:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T18:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T19:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T20:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T21:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T22:00:00Z",
            "score": 0.0085234039,
            "prediction": 0
        }, {
            "datetime": "2020-01-27T23:00:00Z",
            "score": 0.0097708522,
            "prediction": 0
        }]
    }]
}
```

# Frontend Server  Streamlit
* AWS EC2 Auto Scaling
    * Launch Template https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1#LaunchTemplateDetails:launchTemplateId=lt-048cebf301d49c25f
        * komplette Installation des Servers inkl. Stremlit über User Data https://github.com/socialdistancingdashboard/virushack/blob/master/streamlit-beanstalk/install.sh
    * Auto Scaling Group https://eu-central-1.console.aws.amazon.com/ec2/autoscaling/home?region=eu-central-1#AutoScalingGroups:id=sdd-streamlit-scale;view=details
        * Min 2. Server / Max. 10 Server - Scaling bei 60% CPU

* AWS EC2 Loadbalancer
  * Load Balancer https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1#LoadBalancers:sort=loadBalancerName
  * Targt Group https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1#TargetGroups:sort=targetGroupName
