# -*- coding: utf-8 -*-
# Copyright 2018-2019 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example of showing geographic data."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime
import requests
<<<<<<< Updated upstream
import random
=======
from PIL import Image
from io import BytesIO
import boto3
import json
import datetime
>>>>>>> Stashed changes

import pandas as pd

# DATE_TIME = "date/time"
# DATA_URL = (
#     "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
# )

st.title("Social Distancing Dashboard")
#st.markdown("""Hier könnte ihre Werbung stehen.""")

# @st.cache(persist=True)
# def load_data(nrows):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis="columns", inplace=True)
#     data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
#     return data

date = datetime.datetime.now()

@st.cache(persist=True)
def load_mock_data():
<<<<<<< Updated upstream
    county_names = []
    county_ids = []
    mock_scores = []
    gmaps_scores = []
    hystreet_scores = []
    cycle_scores = []
    url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    r = requests.get(url_topojson)
    jsondump = r.json()
    for county in jsondump["objects"]["counties"]["geometries"]:
        county_names.append(county["properties"]["name"])
        county_ids.append(county["id"])
        mock_scores.append(random.randint(0, 100) / 100)
        gmaps_scores.append(random.randint(0, 100) / 100)
        hystreet_scores.append(random.randint(0, 100) / 100)
        cycle_scores.append(random.randint(0, 100) / 100)
    return county_names, county_ids, mock_scores, gmaps_scores, hystreet_scores, cycle_scores


url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'

data = load_data(1000)

county_names, county_ids, mock_scores, gmaps_scores, hystreet_scores, cycle_scores = load_mock_data()
df_mock_scores = pd.DataFrame({"id": county_ids, "name": county_names, "score": mock_scores,"gmap_score": gmaps_scores, "hystreet_score": hystreet_scores, "cycle_score": cycle_scores})
places = st.sidebar.multiselect('Welche Orte?',county_names, ["Bielefeld","Calw"])
date = st.sidebar.date_input('Datum', datetime.date(2011,1,1))



=======
    df = pd.read_csv("scores.csv", index_col = 0, dtype = {"id": str, 'name': str,'date': str,
                                                      'gmap_score': float,'hystreet_score': float, 'cycle_score': float,})
    return df


@st.cache()
def load_s3_data():
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket='sdd-s3-basebucket', Key='googleplaces/{}/{}/{}/{}'.format(str(date.year).zfill(4), str(date.month).zfill(2), str(date.day).zfill(2), str(date.hour-1).zfill(2)))
    bytes_array = response["Body"].read()
    json_data = json.loads(bytes_array)

    return json_data
    # string_array = bytes_array.decode("utf-8")


for i in json_data:
    print(i)
    print(i["address"][""])

#data = load_data(10)
df_mock_scores2 = load_mock_data()
df_mock_scores = df_mock_scores2.copy()
county_names = list(set(df_mock_scores["name"].values))

response = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/logo_with_medium_text.png')
img = Image.open(BytesIO(response.content))
st.sidebar.image(img, use_column_width=True)
places = st.sidebar.multiselect('Welche Orte?',list(set(county_names)), ["Bielefeld","Calw"])
start_date = st.sidebar.date_input('Datum', datetime.date(2020,3,12))
start_date = st.sidebar.date_input('Datum', datetime.date(2020,3,22))
>>>>>>> Stashed changes
data_sources = st.sidebar.multiselect('Welche Daten?',['gmap_score', 'hystreet_score', "cycle_score"],"gmap_score")

#calculate average score based on selected data_sources
if len(data_sources) > 0:
    df_mock_scores["average_score"] = df_mock_scores[data_sources].mean(axis=1)
else:
    df_mock_scores["average_score"] = [0] * len(df_mock_scores)

#filter scores based on selected places
df_mock_scores["filtered_score"] = np.where(df_mock_scores["name"].isin(places),df_mock_scores["average_score"],[0] * len(df_mock_scores))



st.subheader('Social Distancing Map')

data_topojson_remote = alt.topo_feature(url=url_topojson, feature='counties')
c = alt.Chart(data_topojson_remote).mark_geoshape(
    stroke='white'
).encode(
    color=alt.Color('filtered_score:Q', scale=alt.Scale(scheme='greens')),
    tooltip=[alt.Tooltip("properties.name:N", title="Landkreis"),alt.Tooltip("filtered_score:N", title="Score")]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_mock_scores, 'id', ['filtered_score'])
).properties(width=750,height = 1000)
st.altair_chart(c)


<<<<<<< Updated upstream
=======
if len(places) > 0:
    st.subheader("Vergleich Soziale Distanz")
    st.altair_chart(alt.Chart(df_mock_scores[df_mock_scores["name"].isin(places)][["name", "date", "filtered_score"]]).mark_line().encode(
        x= alt.X('date:T',axis = alt.Axis(title = 'Tag', format = ("%d %b"))),
        y= alt.Y('filtered_score:Q',title="Soziale Distanz"),
        color=alt.Color('name',title ="Landkreis")
    ).properties(
        width=750,
        height = 400
    ))
>>>>>>> Stashed changes

st.subheader("Vergleich Soziale Distanz")

st.altair_chart(alt.Chart(df_mock_scores[df_mock_scores["name"].isin(places)][["name","filtered_score"]]).mark_bar(size = 20).encode(
    x='name:N',
    y='filtered_score:Q',
    color=alt.Color('filtered_score:Q', scale=alt.Scale(scheme='greens'))
).properties(width=750,height=400))

if st.checkbox("Show raw data", False):
    st.subheader("Ort gefiltert")
    st.write(df_mock_scores[df_mock_scores["name"].isin(places)])