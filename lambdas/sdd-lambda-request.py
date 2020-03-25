import json
import boto3
import datetime


def lambda_handler(event, context, list_dates=None):
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket='sdd-s3-basebucket',
                               Key='AggregatedData/2020/03/22/sdd-kinese-aggregator-2-2020-03-22-15-28-20-0bb7c782-48b8-4478-8f95-989db4f51834')
    # for date in pd.date_range(event["date_min"], event["date_max"]):
    #      obj = s3.Object('sdd-s3-basebucket',
    #                      'aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2),
    #                                                             str(date.day).zfill(2)))

    event = {}
    try:
        year, month, day = event["min_date"].split("-")
        min_date = datetime.date(int(year), int(month), int(day))
        year, month, day = event["max_date"].split("-")
        max_date = datetime.date(int(year), int(month), int(day))
    except Exception as e:
        print(e)
        # return e
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
                #                date = value["date"]
                value.pop("date")
                dict_response[date_str].update({str(obj_key): value})
        #                dict_response[obj_key].update({date: value})
        except Exception as e:
            print(e)

    # dict_response = {}
    # for landkreis in list_landkreise:
    #     dict_response[landkreis] = {"date": list_dates, "score", list_scores}
    # # {"{landkreis}" : {"date" : ["2020-03-23" , "2020-03-22"] , "score" , [0.231, 0.424]}}

    return {
        'statusCode': 200,
        # 'body': base64.b64encode(list_obj)
        'body': json.dumps(dict_response)
    }


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    min_date = 'min_date'
    max_date = 'max_date'
    try:
        min_date = event[min_date]
        max_date = event[max_date]
    except:
        return "no data... why"

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
                #                date = value["date"]
                value.pop("date")
                dict_response[date_str].update({str(obj_key): value})
        #                dict_response[obj_key].update({date: value})
        except Exception as e:
            print(e)

    # dict_response = {}
    # for landkreis in list_landkreise:
    #     dict_response[landkreis] = {"date": list_dates, "score", list_scores}
    # # {"{landkreis}" : {"date" : ["2020-03-23" , "2020-03-22"] , "score" , [0.231, 0.424]}}

    return {
        'statusCode': 200,
        # 'body': base64.b64encode(list_obj)
        'body': json.dumps(dict_response)
    }
