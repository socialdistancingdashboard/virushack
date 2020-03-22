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
import json
import requests
from PIL import Image
from io import BytesIO


st.title("EveryoneCounts")
st.write("Das Social Distancing Dashboard")

@st.cache(persist=True)
def load_mock_data():
    df = pd.read_csv("/Users/Sebastian/Desktop/scores.csv", index_col = 0, dtype = {"id": str, 'name': str,'date': str,
                                                      'gmap_score': float,'hystreet_score': float, 'cycle_score': float,})
    return df

@st.cache(persist=True)
def load_topojson():
    url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    r = requests.get(url_topojson)
    jsondump = r.json()

    county_names = []
    county_ids = []
    for county in jsondump["objects"]["counties"]["geometries"]:
        county_names.append(county["properties"]["name"])
        county_ids.append(county["id"])

    return county_names, county_ids

@st.cache(persist=True)
def load_real_data(county_names, county_ids):
    response = requests.get('https://3u54czgyw4.execute-api.eu-central-1.amazonaws.com/default/sdd-lambda-request')
    decoded = bytes.decode(response.content, 'utf-8')
    string_fixed = '{"data" : ['+decoded+'] }'
    while True:
        try:
            data_dict = json.loads(string_fixed)
            break;
        except json.decoder.JSONDecodeError as e:
            if not e.args[0].startswith("Expecting ',' delimiter:"):
                raise
            string_fixed = ','.join((string_fixed[:e.pos], string_fixed[e.pos:]))


    county_names_to_id = {name: county_ids[i] for i, name in enumerate(county_names)}
    county_names_prod = []
    county_ids_prod = []
    dates_prod = []
    gmaps_scores_prod = []

    for row in data_dict["data"]:
        if row["name"] in county_names:
            county_names_prod.append(row["name"])
            county_ids_prod.append(county_names_to_id[row["name"]])
            dates_prod.append(row["date"])
            gmaps_scores_prod.append(row["gmap_score"])

    df_mock_scores = pd.DataFrame(
        {"id": county_ids_prod, "name": county_names_prod, "date": dates_prod, "gmap_score": gmaps_scores_prod})

    return df_mock_scores


county_names, county_ids = load_topojson()
df_mock_scores2 = load_real_data(county_names, county_ids)
df_mock_scores = df_mock_scores2.copy()


#df_mock_scores2 = load_mock_data()
#df_mock_scores = df_mock_scores2.copy()
#county_names = list(set(df_mock_scores["name"].values))

response = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/logo_with_medium_text.png')
img = Image.open(BytesIO(response.content))
st.sidebar.image(img, use_column_width=True)
st.sidebar.markdown("")
places = st.sidebar.multiselect('Vergleiche folgende Kreise',options = list(set(county_names)))
#data_sources_dict = {'gmap_score':"Google Popularitätsdaten", "hystreet_score":"Hystreet Daten","cycle_score":"Fahrradzähler Daten"}
data_sources_dict = {'gmap_score':"Google Popularitätsdaten"}
data_sources = st.sidebar.multiselect('mit folgenden Daten',list(data_sources_dict.keys()), format_func=lambda x: data_sources_dict[x], default = ["gmap_score"])
start_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,12))
end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))

#calculate average score based on selected data_sources
if len(data_sources) > 0:
    df_mock_scores["average_score"] = df_mock_scores[data_sources].mean(axis=1)
else:
    df_mock_scores["average_score"] = [0] * len(df_mock_scores)

#filter scores based on selected places
if len(places) > 0:
    df_mock_scores["filtered_score"] = np.where(df_mock_scores["name"].isin(places), df_mock_scores["average_score"],[0] * len(df_mock_scores))
else:
    df_mock_scores["filtered_score"] = df_mock_scores["average_score"]

df_mock_scores["date"] = pd.to_datetime(df_mock_scores["date"])

germany_average = np.mean(df_mock_scores["average_score"])
st.write("Zum Vergleich - die durchschnittliche Soziale Distanz heute in Deutschland:")
st.write(germany_average)



st.subheader('Social Distancing Map')

url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
data_topojson_remote = alt.topo_feature(url=url_topojson, feature='counties')

basemap = alt.Chart(data_topojson_remote).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(width=750,height = 1000)

layer = alt.Chart(data_topojson_remote).mark_geoshape(
    stroke='white'
).encode(
    color=alt.Color('filtered_score:Q', title="Soziale Distanz", scale=alt.Scale(domain=(0, 1),scheme='redyellowgreen')),
    tooltip=[alt.Tooltip("properties.name:N", title="Landkreis"),alt.Tooltip("filtered_score:N", title="Soziale Distanz")]
).transform_lookup(
    lookup='id',
    from_= alt.LookupData(df_mock_scores[df_mock_scores["filtered_score"] > 0], 'id', ['filtered_score'])
).properties(width=750,height = 1000)

c = alt.layer(basemap, layer)
st.altair_chart(c)


if len(places) > 0:
    st.subheader("Vergleich Soziale Distanz")
    st.altair_chart(alt.Chart(df_mock_scores[df_mock_scores["name"].isin(places)][["name", "filtered_score"]]).mark_bar(
        size=20).encode(
        x='name:N',
        y='filtered_score:Q',
        color=alt.Color('filtered_score:Q', title="Soziale Distanz", scale=alt.Scale(domain=(0, 1),scheme='redyellowgreen'))
    ).properties(width=750, height=400))





response = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/Datenquellen.PNG')
img_data_sources = Image.open(BytesIO(response.content))
st.image(img_data_sources, use_column_width=True)

st.markdown("""
    <style type='text/css'>
        details {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)