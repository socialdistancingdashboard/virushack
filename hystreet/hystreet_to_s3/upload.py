import boto3
import pandas as pd
import json
import datetime

df = pd.read_csv('data.csv')

for name, group in df.groupby('timestamp'):
    print(group.to_json(orient='records'))
    date_str = name.split('+')[0]
    date = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
    print(date.year)
    client = boto3.client('s3')
    client.put_object(Body=group.to_json(orient='records'), Bucket='sdd-s3-basebucket',
                      Key='hystreet/'+str(date.year)+'/'+str(date.month)+'/'+str(date.day)+'.json')
