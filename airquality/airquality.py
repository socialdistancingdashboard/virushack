import base64
import os

import boto3
import requests

airquality_token = os.environ['AIR_QUALITY_API_TOKEN']
url = 'https://api.waqi.info/feed/berlin/?token=' + airquality_token

client = boto3.client('firehose')

response = requests.get(url)
if response.status_code == 200:
    # loop over regions
    response = client.put_record(DeliveryStreamName='sdd-kinesis-airquality', Record={'Data': base64.encodebytes(response.content)})