import json
import boto3
import datetime
import base64


def lambda_handler(event, context):
    print(event)

    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket='sdd-s3-basebucket',
                               Key='AggregatedData/2020/03/22/sdd-kinese-aggregator-2-2020-03-22-15-28-20-0bb7c782-48b8-4478-8f95-989db4f51834')
    # for date in pd.date_range(event["date_min"], event["date_max"]):
    #      obj = s3.Object('sdd-s3-basebucket',
    #                      'aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2),
    #                                                             str(date.day).zfill(2)))

    event = {}
    event["min_date"] = "2020-03-20"
    event["max_date"] = "2020-03-23"
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

    for date in dates_list:
        print(date)
        try:
            list_obj = s3_client.get_object(Bucket='sdd-s3-basebucket',
                                            Key=f'aggdata/live/{str(date.year).zfill(4)}/{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/zugdata.json')
            print(list_obj["Body"].read())
        except Exception as e:
            print(e)
    list_dates = [str(x) for x in dates_list]
    dict_response = {}
    for landkreis in list_landkreise:
        dict_response[landkreis] = {"date": list_dates, "score", list_scores}
    # {"{landkreis}" : {"date" : ["2020-03-23" , "2020-03-22"] , "score" , [0.231, 0.424]}}

    return {
        'statusCode': 200,
        'body': base64.b64encode(list_obj)
        'body': json.dumps()
    }

def legacy():

    # event["date_min"], event["date_max"]
    # min_date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    # max_date = datetime.datetime.now().date()

    # pd.date_range(min_date, max_date)
    # datetime.timedelta(days=1)

    s3 = boto3.resource('s3')
    #    obj = s3.Object('sdd-s3-basebucket', 'AggregatedData/2020/03/22/sdd-kinese-aggregator-2-2020-03-22-15-28-20-0bb7c782-48b8-4478-8f95-989db4f51834')
    for date in pd.date_range(event["date_min"], event["date_max"]):
        obj = s3.Object('sdd-s3-basebucket',
                        'aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2),
                                                  str(date.day).zfill(2)))
