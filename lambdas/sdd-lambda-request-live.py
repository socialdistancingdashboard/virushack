import json
import boto3
import datetime

def lambda_handler(event, context):
    list_dates = []
    s3_client = boto3.client('s3')
    min_date = 'min_date'
    max_date = 'max_date'
    min_date = event[min_date]
    max_date = event[max_date]

    try:
        year, month, day = min_date.split("-")
        min_date = datetime.date(int(year), int(month), int(day))
        year, month, day = max_date.split("-")
        max_date = datetime.date(int(year), int(month), int(day))
    except Exception as e:
        print(e)

    difference = max_date - min_date
    dates_list = [min_date + datetime.timedelta(days=x) for x in range(difference.days + 1)]

    list_landkreise = []
    dict_scores = {}
    dict_response = {}
    for date in dates_list:
        try:
            list_obj = s3_client.get_object(Bucket='sdd-s3-basebucket',
                                            Key=f'aggdata/{str(date.year).zfill(4)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}')
            obj = list_obj["Body"].read()

            list_dates = [str(x) for x in dates_list]
            obj_json = json.loads(obj)
            date_str = str(date)
            dict_response[date_str] = {}
            for obj_key, value in obj_json.items():
                value.pop("date")
                dict_response[date_str].update({str(obj_key): value})
        except Exception as e:
            print(e)

    return {
        'statusCode': 200,
        'body': json.dumps(dict_response)
    }
