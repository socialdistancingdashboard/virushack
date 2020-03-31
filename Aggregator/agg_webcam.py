import pandas as pd
from datetime import datetime, date, timedelta
# compatibility with ipython
#os.chdir(os.path.dirname(__file__))
import json
import boto3
from coords_to_kreis import coords_convert
import re

def aggregate(date):
    s3_client = boto3.client('s3')
    data = pd.DataFrame()
    for x in range(0,20):
        try:
            response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='webcamdaten/{}/{}/{}/{}webcamdaten.json'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(x).zfill(2)))
            result = pd.DataFrame(json.loads(response["Body"].read()))
            result["date"] = date
            result["hour"] = x
            data = data.append(result)
        except:
            pass
    #print(data)
    data.columns = [col.lower() for col in data.columns]
    def extract_float(string):
        return re.findall("\d+\.\d+", str(string))[0]
    data["lon"] = data["lon"].apply(extract_float)
    data["lat"] = data["lat"].apply(extract_float)
    #print(data.columns)
    #names(df)[names(df) == 'Lat'] <- 'lat'
    data["ags"] = coords_convert(data)
    #return data
    result = pd.DataFrame(data.groupby("ags")[["personenzahl"]].mean())
    result = result.reset_index()
    list_results = []
    #print(result["personenzahl"])
    #result["personenzahl"] = result[["personenzahl"]] / 2.4
    #print(result["personenzahl"])
    for index, row in result.iterrows():
        landkreis = row['ags']
        relative_popularity = row["personenzahl"]
        data_index = {
            "landkreis": landkreis,
            'webcam_score' : relative_popularity
        }
        list_results.append(data_index)
    return list_results
#aggregate(date.today() - timedelta(days = 2))
