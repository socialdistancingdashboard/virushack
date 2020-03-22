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
from PIL import Image
from io import BytesIO


DATE_TIME = "date/time"
DATA_URL = (
    "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

st.title("Social Distancing Dashboard")
#st.markdown("""Hier könnte ihre Werbung stehen.""")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

@st.cache()
def load_mock_data():
    df = pd.read_csv("/Users/Sebastian/Desktop/scores.csv", index_col = 0, dtype = {"id": str, 'name': str,'date': str,
                                                      'gmap_score': float,'hystreet_score': float, 'cycle_score': float,})
    return df


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
data_sources = st.sidebar.multiselect('Welche Daten?',['gmap_score', 'hystreet_score', "cycle_score"],"gmap_score")

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




st.subheader('Social Distancing Map')

url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
data_topojson_remote = alt.topo_feature(url=url_topojson, feature='counties')
st.altair_chart(alt.Chart(data_topojson_remote).mark_geoshape(
    stroke='white'
).encode(
    color=alt.Color('filtered_score:Q', title="Soziale Distanz", scale=alt.Scale(scheme='redyellowgreen')),
    tooltip=[alt.Tooltip("properties.name:N", title="Landkreis"),alt.Tooltip("filtered_score:N", title="Score")]
).transform_lookup(
    lookup='id',
    from_= alt.LookupData(df_mock_scores, 'id', ['filtered_score'])
).properties(width=750,height = 1000))





if len(places) > 0:
    st.subheader("Vergleich Soziale Distanz")
    st.altair_chart(alt.Chart(df_mock_scores[df_mock_scores["name"].isin(places)][["name","date", "filtered_score"]]).mark_line().encode(
        x= alt.X('date:T',axis = alt.Axis(title = 'Tag', format = ("%d %b"))),
        y= alt.Y('filtered_score:Q',title="Soziale Distanz"),
        color=alt.Color('name',title ="Landkreis")
    ).properties(
        width=750,
        height = 400
    ))



if st.checkbox("Show raw data", False):
    st.subheader("Ort gefiltert")
    st.write(df_mock_scores[df_mock_scores["name"].isin(places)])
