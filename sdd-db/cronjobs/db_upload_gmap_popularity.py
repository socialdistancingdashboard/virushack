
""" This script uploads into database from s3 bucket source
This should be run daily on any machine that meets the python dependencies.
"""

try:  # allows to import local modules
  __IPYTHON__ 
  os.chdir(os.path.dirname(__file__))
except: pass
import boto3
import json
from datetime import datetime, timedelta
import pandas as pd
import pymysql 
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import dateutil.parser
from shapely.geometry import Point, Polygon
from shapely import wkt

# ask for credentials
config = json.load(open("../../credentials/credentials-aws-db.json", "r"))

aws_engine = create_engine(
  ("mysql+pymysql://" +
  config["user"] + ":" +
  config["password"] + "@" +
  config["host"] + ":" + 
  str(config["port"]) + "/" +
  config["database"]),
  poolclass=NullPool, # dont maintain a pool of connections
  pool_recycle=3600 # handles timeouts better, I think...
)

# pymysql connection for queries outside of pandas (easier to use in that case)
pymysql_con = pymysql.connect(
  config["host"], 
  config["user"], 
  config["password"], 
  config["database"])

## SOURCE_ID ANPASSEN!
source_id = "score_google_places"
s3_client = boto3.client('s3')

# load locations (the geometry is saved in db and transforemd to WKT format for mapping of coords to district)
q = """ SELECT district_id, ASWKT(geometry) AS geometry from locations """
locations = pd.read_sql(q, aws_engine)
locations["geometry"] = locations["geometry"].apply(wkt.loads)

def coords_to_district_id(lat, lon):
  """ transforms lat lon to district id without(!) geopandas """
  point = Point(float(lon), float(lat))
  for i, district in locations.iterrows():
    shape = district["geometry"]
    if point.within(shape):
      return district["district_id"]
  return None


def custom_index(x):
  """ used to merge foreign station keys on scores """
  return (str(x["district_id"]) + str(x["description"]) + str(x["source_station_id"]))


def upload_date(date):
  """ Uploads data for given date """
  print("processing", date)

  stations = []
  scores = []

  ## ANPASSEN WENN NUR TAGEWEISE
  for hour in range(0,24):
    try:
      response = s3_client.get_object(
        ## BUCKET NAMEN ANPASSEN AUCH: PFAD ANPASSEN
        Bucket='sdd-s3-bucket', 
        Key='googleplaces/{}/{}/{}/{}'.format(
          str(date.year).zfill(4),
          str(date.month).zfill(2),
          str(date.day).zfill(2),
          str(hour).zfill(2)))
      
      result = json.loads(response["Body"].read())
    except:
      continue


    ## CHECKEN OB DIE JSON EINE LISTE AUS STATIONEN IST
    for station in result:
      score_value = station["current_popularity"]
  
      try:
        score_reference = station["populartimes"][date.weekday()]["data"][hour]
      except:
        ## REFERENCE VALUE NONE WENN NICHT MITGELIEFERT
        score_reference = None


      coordinates = pd.DataFrame([station["coordinates"]])

      ## CHECKEN OB LON LAT SO HEISSEN
      coordinates.rename(columns={"lng": "lon"}, inplace=True)
      district_id = coords_to_district_id(coordinates["lat"], coordinates["lon"])


      ## ANPASSEN, DASS FÜR JEDE STATION DIE ZUSATZINFOS ABGESPEICHERT WERDEN
      other = {
        "googleplaces_id": station["id"],
        "station_name": station["name"],
        "address": station["address"],
        "station_types": station["types"],
        "station_lon": station["coordinates"]["lng"],
        "station_lat": station["coordinates"]["lat"],
        "station_rating": station["rating"],
        "station_rating_n": station["rating_n"]
      }

      ## ANPASSEN
      stations.append({
        "district_id": district_id,
        "source_id": source_id,
        "other": json.dumps(other),
        "description": station["name"][0:128],
        "source_station_id": station["id"],
      })

      other = {
        # dont loose this information
        "populartimes": station["populartimes"]
      }

      ## ANPASSEN, DASS FÜR JEDEN DATENPUNKT DIE ZUSATZINFOS ABGESPEICHERT WERDEN
      scores.append({
        "dt": datetime(date.year, date.month, date.day, hour),
        "score_value": score_value,
        "reference_value": score_reference,
        "source_id": source_id,
        "district_id": district_id,
        "source_station_id": station["id"],
        "description": station["name"],
        "other": json.dumps(other)
      })

  
  # upload stations. handles duplicates so dont worry
  if len(stations) > 0:
    q = """
      INSERT INTO stations 
      (
        district_id,
        source_id,
        other,
        description,
        source_station_id
      )
      VALUES (%s, %s, %s, %s, %s )
      ON DUPLICATE KEY UPDATE
      other = VALUES(other),
      description = VALUES(description)
    """
    df_stations = pd.DataFrame(stations).drop_duplicates()

    with pymysql_con.cursor() as cur:
      cur.executemany(
        ## DARAUF ACHTEN, DASS DIE SPALTEN IM DATAFRAME GENAU DER REIHENFOLGE DES INSERTS ENTSPRECHEN
        q, df_stations[["district_id", "source_id", "other", "description", "source_station_id" ]].values.tolist()) 
    pymysql_con.commit()

  # upload scores
  if len(scores) > 0:
    q = """
      SELECT id AS station_id, district_id, description, source_station_id FROM stations 
      WHERE source_id = '%s' 
    """ % source_id
    
    scores_stations_foreign_keys = pd.read_sql(q, aws_engine) 
    scores_stations_foreign_keys["custom_index"] = scores_stations_foreign_keys.apply(custom_index, axis=1)
    scores_stations_foreign_keys.drop(["district_id", "description", "source_station_id"], axis=1, inplace=True)
    
    df_scores = pd.DataFrame(scores)
    df_scores["custom_index"] = df_scores.apply(custom_index, axis=1)
    
    df_scores = df_scores.merge(
      scores_stations_foreign_keys,
      on="custom_index",
      how="left",
      suffixes=(False, False)
    )
    df_scores.drop(["description", "source_station_id", "custom_index"], axis=1, inplace=True)
    df_scores['dt'] = df_scores['dt'].astype(str)
    q = """
      INSERT INTO scores 
      (
        dt,
        score_value,
        reference_value,
        source_id,
        district_id,
        station_id,
        other
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
      score_value = VALUES(score_value),
      reference_value = VALUES(reference_value),
      other = VALUES(other)

    """
    df_scores = df_scores.drop_duplicates()

    with pymysql_con.cursor() as cur:
      ## DARAUF ACHTEN, DASS DIE SPALTEN IM DATAFRAME DER REIHENFOLGE DES INSERTS ENTSPRECHEN
      cur.executemany(q, df_scores[["dt", "score_value", "reference_value", "source_id", "district_id", "station_id", "other"]].values.tolist()) 
    pymysql_con.commit()

    print("upload completed")

def upload_all():
  """ drops all existent data and replaces it by s3 bucket content """
  # delete all 
  first_date_available = datetime(2020, 3, 22) # used in get-all-data mode  
  now = datetime.now()
  d = first_date_available

  # delete all before uploading all
  for table in ["scores", "stations"]:
    q = """
      DELETE FROM %s WHERE source_id = '%s';
    """ % (table, source_id )
    with pymysql_con.cursor() as cur:
      cur.execute(q) 
    pymysql_con.commit()

  # delete source
  with pymysql_con.cursor() as cur:
    cur.execute("DELETE FROM sources WHERE id = '%s'" % source_id) 
  pymysql_con.commit()

  ## DIE ERSTELLUNG DER QUELLE ANPASSEN!
  # recreate source
  q = """
  INSERT INTO sdd.sources (
    id, /* frei wählbar: 'score_xy', siehe VALUES */
    desc_short, /* siehe VALUES */
    desc_long, contributors, /* siehe VALUES */
    unit, /* 'Anzahl' oder 'Prozent', nichts anderes(!) */
    unit_long, /* Einheit für Frontend, frei wählbar */
    unit_agg_long, /* Einheit nach aggregation, 'Anzahl' oder 'Prozent' */
    sample_interval, /* 'hourly' oder 'daily' */
    agg_mode, /* wie soll aggregiert werde? 'sum', 'avg-percentage-of-normal' */
    has_reference_values /* '0' für nicht vorhanden, '1' für vorhanden */
  ) VALUES (
    '%s',
    "Passantenfrequenz in Lemgo",
    "Entspricht der Anzahl an Passanten in Lemgo",
    "Fraunhofer IOSB-INA",
    "Anzahl",
    "Anzahl Passanten",
    "Prozent vom Normalwert",
    "daily",
    "avg-percentage-of-normal",
    1
  )
  """ % source_id

  print("all existing data dropped")

  # upload until yesterday (including)
  while d < datetime(now.year, now.month, now.day):
    upload_date(d)
    d = d + timedelta(days=1)
  

# use this for intial upload
# upload_all()

# upload this for timed upload (e.g. cronjob)
upload_date(datetime.now() - timedelta(days=1))

# free connection
pymysql_con.close()