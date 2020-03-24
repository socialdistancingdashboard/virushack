import boto3
import pandas as pd
from datetime import date, timedelta
from agg_hystreet import aggregate as agg_hystreet
from agg_gmapscore import aggregate as agg_gmapscore
from agg_zugdaten import aggregate as agg_zugdaten
import json

date = date.today() - timedelta(days = 1)

list_result = pd.DataFrame(columns = ['landkreis'])
list_result =list_result.set_index("landkreis")

gmapscore_list = pd.DataFrame(agg_gmapscore(date))
gmapscore_list = gmapscore_list.set_index('landkreis')
list_result = list_result.join(gmapscore_list, how = "outer")

hystreet_list = pd.DataFrame(agg_hystreet(date))
hystreet_list = hystreet_list.set_index('landkreis')
list_result = list_result.join(hystreet_list, how = "outer")

zugdaten_list = pd.DataFrame(agg_zugdaten(date))
zugdaten_list = zugdaten_list.set_index('landkreis')
list_result = list_result.join(zugdaten_list, how = "outer")


list_result["date"] = str(date)
list_result.to_csv("test.csv")

dict = list_result.T.to_dict()

s3_client = boto3.client('s3')
s3_client.put_object(Bucket='sdd-s3-basebucket', Key="aggdata/live", Body=json.dumps(dict))
s3_client.put_object(Bucket='sdd-s3-basebucket', Key='aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2)), Body=json.dumps(dict))
