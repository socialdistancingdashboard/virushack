
# Database und (GET) API Spezifikation

# Server
* AWS
* mysql db auf AWS
* lambdas exposen API
* Weitere Anforderungen:
    * Tensorflow
    * Cronjobs

# Datenbank "sdd" (social distancing dashboard)
## Tabelle locations

```sql
/* Contains meta information for all amtliche Gemeindeschlüssel */
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
  landkreis_id VARCHAR(5) PRIMARY KEY, /* landkreis_id */
  landkreis VARCHAR(128) NOT NULL,
  landkreis_type VARCHAR(128) NOT NULL,
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
  landkreis_id VARCHAR(32) NOT NULL, /* regional identifier */
  category VARCHAR(64) NOT NULL, /* which source */
  meta TEXT NULL, /* stringified JSON dump with additional characteristics */
  description TEXT NULL, /* BHF Name, Webcam Standort, etc */
  source_id VARCHAR(128), /* Dient dazu innerhalb eines Landkreises Quellen zu unterscheiden. Bspw. "Webcam Marktplatz" */
  INDEX(category),
  INDEX(landkreis_id),
  UNIQUE(landkreis_id, category, source_id) /* Meta Daten sind zeitunabhängig */
);

```
## Tabelle scores
```sql
/* Contains the actual data */
DROP TABLE IF EXISTS scores;
CREATE TABLE  scores (
  id INT UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
  dt DATETIME NOT NULL,
  score_value DOUBLE NOT NULL, /* social distancing measure */
  reference_value DOUBLE NULL, /* expected value without corona */
  category VARCHAR(32) NOT NULL,
  landkreis_id VARCHAR(32) NOT NULL, /* regional identifier */
  meta_id INT UNSIGNED NOT NULL,
  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX(category),
  INDEX(dt),
  INDEX(landkreis_id)
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
* returns 
```javascript
 [{
    "landkreis_id": string, /* 5stellige Landkreis Id "01234567" */
    "landkreis": string, /* "Kreis Karlsruhe" */
    "landkreis_type": string, /* "Stadtkreis" */
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
* Endpoint
  * https://ywn1ye2l46.execute-api.eu-central-1.amazonaws.com/Prod/get-categories
* returns
```javascript
 [{
    "name": string,
    "desc_short": text,
    "desc_long": text
  }]
```

## get_spatial_data(opt)
Liefert alle Infos für Plot auf Landkarte in verschiednen Granularitäten.

Optionen bzw Filter.
```javascript
opt = {
    "date": datetime /*[2020-03-22]*/
    "categories": string[] /* ["public_transportation_ice", "webcams"]*/
    "spatial_granularity": /* 1: country, 2: state, 3: district*/
}
```
Rückgabe
```javascript
res = {
    "request": {
        /*gespiegelte Request options, see above*/
    },
    "values": [
        {
            "ags": string /* "001234" OR "BW" OR "DE"*/
            "score": float /* 0.12 */
        }
    ]
}
```

## get_time_series(options)
Liefert Daten für Darstellung in Zeitreihe. Keine zeitliche Aggregation.
```javascript
opt = {
    "start_date": datetime /*[2020-03-22] */
    "end_date": datetime /*[2020-03-22]*/
    "timeline-specs": [{
      "categories": string /* ["public_transportation_ice", "webcams"]*/
      "spatial_level": string /* "country" / "state" / "district" */
      "spatial_identifier": string /* according to spatial level "DE" or "BW" or "01234567"
    }]
}
```
Aggregate on spatial level but not on temporal level.
```javascript
result = [
    {
       "request" = {
          "start_date": datetime /*[2020-03-22] */
          "end_date": datetime /*[2020-03-22]*/
          "timeline-specs": [{
            "categories": string /* ["public_transportation_ice", "webcams"]*/
            "spatial_level": string /* "country" / "state" / "district" */
            "spatial_identifier": string /* according to spatial level "DE" or "BW" or "01234567" */
      },        
      "timelines": [
          "category": string,
          "description_short": string,
          "description_long": string,
          "values": [
            {
                "datetime": datetime
                "value_reference": number,
                "value_absolute": number,
                "value_score": number,
                "spational_level": string,
                "spatial_identifier": string,
                "spatial_identifier_userfriendly": string
            }
         ]
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
  
## get_all()
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

