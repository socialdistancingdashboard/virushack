import json
import boto3
import datetime


def lambda_handler(event, context, list_dates=None):
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


dict_response = {}
dict_response["obj_key"] = {}
dict_response.update({"date" : {} })

dict_response["date"].update({"obj_key2": "value2"})
dict_response["obj_key"].update({"date": "value"})

json.loads("{\"2020-03-23\": {\"01001\": {\"gmap_score\": 0.407620200414234, \"hystreet_score\": 0.0010493513100992117}, \"01003\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00022503132538336304}, \"02000\": {\"gmap_score\": 0.33152974063611157, \"hystreet_score\": 0.00017822854687875504}, \"03101\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0006436597329719818}, \"03152\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0006978622583598082}, \"03241\": {\"gmap_score\": 0.2838892076463815, \"hystreet_score\": 0.0005844901170486463}, \"03254\": {\"gmap_score\": 0.4739075418436469, \"hystreet_score\": 0.0}, \"03351\": {\"gmap_score\": NaN, \"hystreet_score\": 0.001014113073607707}, \"03402\": {\"gmap_score\": 0.5140493339758591, \"hystreet_score\": NaN}, \"03403\": {\"gmap_score\": 0.36761097568473217, \"hystreet_score\": 0.000589699923334067}, \"03404\": {\"gmap_score\": 0.4339899687195537, \"hystreet_score\": 0.0006053563772177371}, \"04011\": {\"gmap_score\": 0.37447916013528626, \"hystreet_score\": 0.0003576614662689471}, \"04012\": {\"gmap_score\": 0.40531276800676136, \"hystreet_score\": NaN}, \"05111\": {\"gmap_score\": 0.3259966345257922, \"hystreet_score\": 0.0003554780457704173}, \"05112\": {\"gmap_score\": 1.0585700748526832, \"hystreet_score\": NaN}, \"05113\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0007394671126109817}, \"05114\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0005147204050729886}, \"05116\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0005390275173547611}, \"05117\": {\"gmap_score\": 0.4454931730655404, \"hystreet_score\": NaN}, \"05122\": {\"gmap_score\": 0.4752184300643205, \"hystreet_score\": NaN}, \"05124\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0013167742243148737}, \"05158\": {\"gmap_score\": 0.4745141203945443, \"hystreet_score\": NaN}, \"05162\": {\"gmap_score\": 0.487237130185674, \"hystreet_score\": NaN}, \"05170\": {\"gmap_score\": 0.2411303374437837, \"hystreet_score\": NaN}, \"05314\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0004569948462100954}, \"05315\": {\"gmap_score\": 0.18615339019667984, \"hystreet_score\": 0.00037400941299147394}, \"05316\": {\"gmap_score\": 0.42072221513885805, \"hystreet_score\": NaN}, \"05334\": {\"gmap_score\": 0.6039232388339937, \"hystreet_score\": 0.0006124068799078167}, \"05362\": {\"gmap_score\": 0.44509231411862993, \"hystreet_score\": NaN}, \"05374\": {\"gmap_score\": 0.41481525389821317, \"hystreet_score\": NaN}, \"05378\": {\"gmap_score\": 0.3719632374883853, \"hystreet_score\": 0.00019115975348038192}, \"05515\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0004008998345414197}, \"05554\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0007638446849140675}, \"05562\": {\"gmap_score\": 0.3221714195824671, \"hystreet_score\": NaN}, \"05711\": {\"gmap_score\": 0.3209198649459533, \"hystreet_score\": 0.0004337127415904673}, \"05754\": {\"gmap_score\": 0.560740109164432, \"hystreet_score\": NaN}, \"05758\": {\"gmap_score\": 0.29715125512816776, \"hystreet_score\": NaN}, \"05770\": {\"gmap_score\": 0.35159727284850695, \"hystreet_score\": NaN}, \"05774\": {\"gmap_score\": 0.3469681487917929, \"hystreet_score\": 0.0005071545009961964}, \"05911\": {\"gmap_score\": 0.2733594258930983, \"hystreet_score\": NaN}, \"05913\": {\"gmap_score\": 0.3055584748527401, \"hystreet_score\": 0.00018648612604766696}, \"05914\": {\"gmap_score\": 0.39457825963504406, \"hystreet_score\": NaN}, \"05916\": {\"gmap_score\": 0.43980085732601987, \"hystreet_score\": NaN}, \"05954\": {\"gmap_score\": 0.3962345277159479, \"hystreet_score\": NaN}, \"05958\": {\"gmap_score\": NaN, \"hystreet_score\": 0.000380119737717381}, \"05962\": {\"gmap_score\": 0.4207768932982253, \"hystreet_score\": NaN}, \"05978\": {\"gmap_score\": 0.4117930766077735, \"hystreet_score\": NaN}, \"06411\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00011222408512840766}, \"06412\": {\"gmap_score\": 0.3792579305863007, \"hystreet_score\": 0.00044562538067204}, \"06414\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0004649619470915573}, \"06433\": {\"gmap_score\": 0.1401779929596837, \"hystreet_score\": NaN}, \"06531\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0005731830498148177}, \"06533\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0003411227541059944}, \"06611\": {\"gmap_score\": 0.41518779873374134, \"hystreet_score\": NaN}, \"07111\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0}, \"07211\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00037543981089424626}, \"07314\": {\"gmap_score\": 0.8538600800121541, \"hystreet_score\": NaN}, \"07315\": {\"gmap_score\": 0.28189315850150254, \"hystreet_score\": 0.0003228474943514687}, \"07318\": {\"gmap_score\": 0.5125815694448046, \"hystreet_score\": NaN}, \"07319\": {\"gmap_score\": 0.44219829031028557, \"hystreet_score\": NaN}, \"08111\": {\"gmap_score\": 0.37534586499110567, \"hystreet_score\": 0.00045055323372937697}, \"08118\": {\"gmap_score\": 3.0, \"hystreet_score\": NaN}, \"08121\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0002914339038699871}, \"08136\": {\"gmap_score\": 0.5325116572395482, \"hystreet_score\": NaN}, \"08212\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00039645549987156096}, \"08221\": {\"gmap_score\": 0.33324380018691974, \"hystreet_score\": 0.0006555792108548024}, \"08222\": {\"gmap_score\": 1.2484175765754715, \"hystreet_score\": 0.0007118179899915465}, \"08231\": {\"gmap_score\": 0.4489222416464783, \"hystreet_score\": NaN}, \"08311\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00018092898509838078}, \"08317\": {\"gmap_score\": 0.3378100174721689, \"hystreet_score\": NaN}, \"08326\": {\"gmap_score\": 1.0325812884655763, \"hystreet_score\": NaN}, \"08415\": {\"gmap_score\": 0.3320792521909351, \"hystreet_score\": 0.0006258373018589323}, \"08416\": {\"gmap_score\": 0.4203184873341613, \"hystreet_score\": NaN}, \"08421\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0008782451633536005}, \"08426\": {\"gmap_score\": NaN, \"hystreet_score\": 0.002402803270482229}, \"09161\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0002730814023533191}, \"09162\": {\"gmap_score\": 0.22481598992118107, \"hystreet_score\": 0.0005849499364063272}, \"09261\": {\"gmap_score\": 0.3524532531576151, \"hystreet_score\": NaN}, \"09262\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00030931194662159556}, \"09461\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0008997020168511964}, \"09562\": {\"gmap_score\": NaN, \"hystreet_score\": 0.000656537349072398}, \"09564\": {\"gmap_score\": 0.37734723296277617, \"hystreet_score\": 0.0003708928341528768}, \"09663\": {\"gmap_score\": 0.3067559202494087, \"hystreet_score\": 0.0003425855694225586}, \"09761\": {\"gmap_score\": 0.370853733127362, \"hystreet_score\": 0.0008282873728667857}, \"10041\": {\"gmap_score\": NaN, \"hystreet_score\": 0.0002921614247489103}, \"11000\": {\"gmap_score\": 0.265959712293696, \"hystreet_score\": 0.0002629276624897583}, \"12054\": {\"gmap_score\": 0.7418756451084036, \"hystreet_score\": NaN}, \"13003\": {\"gmap_score\": 0.5445090989251987, \"hystreet_score\": 0.0004653151397361596}, \"13004\": {\"gmap_score\": 0.5322233365820476, \"hystreet_score\": NaN}, \"13075\": {\"gmap_score\": 0.4832131360409416, \"hystreet_score\": NaN}, \"14511\": {\"gmap_score\": 0.4331828164394005, \"hystreet_score\": NaN}, \"14523\": {\"gmap_score\": 0.4887891450955257, \"hystreet_score\": NaN}, \"14612\": {\"gmap_score\": 0.3201313670399692, \"hystreet_score\": 0.00018291284673584626}, \"14713\": {\"gmap_score\": Infinity, \"hystreet_score\": 0.0003777231560271302}, \"15003\": {\"gmap_score\": 0.4398100407304212, \"hystreet_score\": NaN}, \"16051\": {\"gmap_score\": NaN, \"hystreet_score\": 0.00046199099973089406}, \"16052\": {\"gmap_score\": 0.5334509737532028, \"hystreet_score\": NaN}, \"16053\": {\"gmap_score\": 0.3311558369167066, \"hystreet_score\": NaN}}}")
