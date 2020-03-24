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
import urllib
import json
import requests
from PIL import Image
from io import BytesIO


st.title("#EveryoneCounts - Das Social Distancing Dashboard")

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
def load_real_data(county_names, county_ids,history_length=5):

    min_date = datetime.datetime.now().date() - datetime.timedelta(days=history_length)
    max_date = datetime.datetime.now().date()
    params = {"min_date": str(min_date), "max_date": str(max_date), "data_sources":"0,1,2"}
    response = requests.get('https://f3fp7p5z00.execute-api.eu-central-1.amazonaws.com/dev/sdd-lambda-request',params = params)

    county_names_prod = []
    county_ids_prod = []
    dates_prod = []
    gmaps_scores_prod = []
    hystreet_scores_prod = []
    zug_scores_prod = []

    data_dict = json.loads(dict(response.json())["body"])

    for (date, row) in list(data_dict.items()):
        print(date)
        for cid, scores in row.items():
            county_names_prod.append(id_to_name[cid])
            county_ids_prod.append(cid)
            dates_prod.append(date)
            if "gmap_score" in scores:
                gmaps_scores_prod.append(scores["gmap_score"])
            else:
                gmaps_scores_prod.append(np.nan)
            hystreet_scores_prod.append(scores["hystreet_score"])
            zug_scores_prod.append(scores["zug_score"])


    df_mock_scores = pd.DataFrame(
        {"id": county_ids_prod, "name": county_names_prod, "date": dates_prod, "gmap_score": gmaps_scores_prod, "hystreet_score": hystreet_scores_prod, "zug_score": zug_scores_prod})

    return df_mock_scores

county_names, county_ids = load_topojson()
id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
df_mock_scores_full = load_real_data(county_names, county_ids)
df_mock_scores = df_mock_scores_full.copy()

# filter for yesterday's entries, so that only on day's worth of data is in df_mock_scores:
# I guess this is relevant for the averaging
date_yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
df_mock_scores = df_mock_scores[df_mock_scores["date"] == date_yesterday]

response = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/logo_with_medium_text.png')
img = Image.open(BytesIO(response.content))
st.sidebar.image(img, use_column_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.subheader("Datenfilter")
available_countys = [value for value in county_names if value in df_mock_scores["name"]]
countys = st.sidebar.multiselect('Vergleiche folgende Kreise',options = list(set(county_names)))
data_sources_names = {'gmap_score':"Google Popularitätsdaten","hystreet_score":"Hystreet Daten", "zug_score":"Zug Daten"}
available_data_sources = [value for value in df_mock_scores.columns if value in data_sources_names.keys()]
data_sources = st.sidebar.selectbox('mit folgenden Daten',available_data_sources, format_func=lambda x: data_sources_names[x])
print(data_sources)
#start_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,12))
#end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))

st.sidebar.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("weitere Infos")
st.sidebar.markdown("<a href='https://twitter.com/distancingdash/'>https://twitter.com/distancingdash/</a>", unsafe_allow_html=True)
st.sidebar.markdown("<a href='https://www.youtube.com/watch?v=pDgcbE-c31c&feature=youtu.be'>https://www.youtube.com/watch?v=pDgcbE-c31c&feature=youtu.be</a>", unsafe_allow_html=True)
st.sidebar.markdown("<a href='https://devpost.com/software/12-social-distancing-dashboard'>https://devpost.com/software/12-social-distancing-dashboard</a>", unsafe_allow_html=True)


#calculate average score based on selected data_sources
if len(data_sources) > 0:
    df_mock_scores["average_score"] = df_mock_scores[[data_sources]].mean(axis = 1)
else:
    df_mock_scores["average_score"] = [0] * len(df_mock_scores)

#filter scores based on selected places
if len(countys) > 0:
    df_mock_scores["filtered_score"] = np.where(df_mock_scores["name"].isin(countys), df_mock_scores["average_score"],[0] * len(df_mock_scores))
else:
    df_mock_scores["filtered_score"] = df_mock_scores["average_score"]

df_mock_scores["date"] = pd.to_datetime(df_mock_scores["date"])

germany_average = np.mean(df_mock_scores["average_score"])
st.write("Zum Vergleich - die durchschnittliche Soziale Distanz heute in Deutschland: {0:.2f}".format(germany_average))



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
    color=alt.Color('filtered_score:Q', title="Soziale Distanz", scale=alt.Scale(domain=(2, 0),scheme='redyellowgreen')),
    tooltip=[alt.Tooltip("properties.name:N", title="Landkreis"),alt.Tooltip("filtered_score:N", title="Soziale Distanz")]
).transform_lookup(
    lookup='id',
    from_= alt.LookupData(df_mock_scores[df_mock_scores["filtered_score"] > 0], 'id', ['filtered_score'])
).properties(width=750,height = 1000)

c = alt.layer(basemap, layer).configure_view(
    strokeOpacity=0
)
st.altair_chart(c)


if len(countys) > 0:

    st.altair_chart(alt.Chart(df_mock_scores[df_mock_scores["name"].isin(countys)][["name","average_score"]]).mark_bar(size = 20).encode(
        x = alt.X('name:N', title="Landkreis / Kreisfreie Stadt"),
        y = alt.Y('average_score:Q', title="Soziale Distanz"),
        color=alt.Color('average_score:Q', title="Soziale Distanz",
                        scale=alt.Scale(domain=(2, 0), scheme='redyellowgreen')),
    ).properties(width=750,height=400))


#-------------

if len(countys) > 0:
    st.subheader('Zeitliche Entwicklung')
    df_history_scores = df_mock_scores_full.copy()
    df_history_scores["date"] = pd.to_datetime(df_history_scores["date"])
    df_history_scores = df_history_scores[df_history_scores["name"].isin(countys)]

    df_history_scores2 = pd.DataFrame()
    for county in countys:
        df_temp = df_history_scores[df_history_scores["name"].isin([county])][["date",data_sources]]
        df_history_scores2["date"] = df_temp["date"].reset_index(drop=True)
        df_history_scores2[county] = df_temp[data_sources].reset_index(drop=True)
    df_history_table = df_history_scores2.copy()
    df_history_scores2 = df_history_scores2.melt("date")
    df_history_scores2 = df_history_scores2.rename(columns = {'variable':'Stadt/Landkreis'})

    st.altair_chart(alt.Chart(  df_history_scores2 ).mark_line().mark_line(point=True).encode(
        x = alt.X('date:T', title="Datum"),
        y = alt.Y('value:Q', title=data_sources),
        color='Stadt/Landkreis:N'
    ).properties(width=750,height=400))
    check_show_raw_history = st.checkbox('Rohdaten anzeigen', value=False)
    if check_show_raw_history:
        st.write(df_history_table)
