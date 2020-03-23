import boto3
import pandas as pd
from datetime import date
from agg_hystreet import aggregate as agg_hystreet
from agg_gmapscore import aggregate as agg_gmapscore
import json

date = date.today()

list_result = pd.DataFrame(columns = ['name'])
list_result =list_result.set_index("name")

gmapscore_list = pd.DataFrame(agg_gmapscore())
gmapscore_list = gmapscore_list.set_index('name')
list_result = list_result.join(gmapscore_list, how = "outer")

hystreet_list = pd.DataFrame(agg_hystreet())
hystreet_list = hystreet_list.set_index('name')
list_result = list_result.join(hystreet_list, how = "outer")

list_result["date"] = date
list_result.to_csv("test.csv")

dict = list_result.T.to_dict()

s3_client = boto3.client('s3')
s3_client.put_object(Bucket='sdd-s3-basebucket', Key="aggdata/live", Body=json.dumps(dict))
s3_client.put_object(Bucket='sdd-s3-basebucket', Key='aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), Body=json.dumps(dict)))
