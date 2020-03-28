import boto3
import pandas as pd
from datetime import date, timedelta
from agg_webcam import aggregate as agg_webcam
from agg_hystreet import aggregate as agg_hystreet
from agg_gmap_transit_score import aggregate as agg_gmap_transit_score
from agg_zugdaten import aggregate as agg_zugdaten
from agg_fahrrad import aggregate as agg_fahrrad
from agg_airquality import aggregate as agg_airquality
from agg_lemgo_digital import aggregate as agg_lemgo_digital
import json


s3_client = boto3.client('s3')
for x in range(0,2):
    print(x)
    date = date.today() - timedelta(days=x)
    list_result = pd.DataFrame(columns=['landkreis'])
    list_result = list_result.set_index("landkreis")

    try:
        lemgo_digital_list = pd.DataFrame(agg_lemgo_digital(date))
        lemgo_digital_list = lemgo_digital_list.set_index('landkreis')
        list_result = list_result.join(lemgo_digital_list, how="outer")
    except Exception as e:
        print(e)
    try:
        gmapscore_list = pd.DataFrame(agg_gmap_transit_score(date))
        gmapscore_list = gmapscore_list.set_index('landkreis')
        list_result = list_result.join(gmapscore_list, how="outer")
    except Exception as e:
        print(e)
    try:
        webcam_list = pd.DataFrame(agg_webcam(date))
        webcam_list = webcam_list.set_index('landkreis')
        list_result = list_result.join(webcam_list, how="outer")
    except Exception as e:
        print(e)

    try:
        hystreet_list = pd.DataFrame(agg_hystreet(date))
        hystreet_list = hystreet_list.set_index('landkreis')
        list_result = list_result.join(hystreet_list, how = "outer")
    except Exception as e:
        print(e)

    try:
        zugdaten_list = pd.DataFrame(agg_zugdaten(date))
        zugdaten_list = zugdaten_list.set_index('landkreis')
        list_result = list_result.join(zugdaten_list, how="outer")
    except Exception as e:
        print(e)

    try:
        fahrrad_list = pd.DataFrame(agg_fahrrad(date))
        fahrrad_list = fahrrad_list.set_index('landkreis')
        list_result = list_result.join(fahrrad_list, how="outer")
    except Exception as e:
        print(e)

    try:
        airquality_list = pd.DataFrame(agg_airquality(date))
        airquality_list = airquality_list.set_index('landkreis')
        list_result = list_result.join(airquality_list, how="outer")
    except Exception as e:
        print(e)

    list_result["date"] = str(date)
    # list_result.to_csv("test.csv")

    dict = list_result.T.to_dict()

    # s3_client.put_object(Bucket='sdd-s3-basebucket', Key="aggdata/live", Body=json.dumps(dict))
    response = s3_client.put_object(Bucket='sdd-s3-basebucket',
                                    Key='aggdata/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2),
                                                                  str(date.day).zfill(2)), Body=json.dumps(dict))
    print(response)
