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
import pydeck as pdk
import datetime
import requests
import geopandas as gpd
import json


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


data = load_data(1000)

city = st.sidebar.text_input('Gib deinen Ort an', 'Berlin')

hour = 2

date = st.sidebar.date_input('Datum', datetime.date(2011,1,1))

options = st.sidebar.multiselect('Welche Daten?',('Hystreet', 'Maps', "Fahrrad Count"))

data = data[data[DATE_TIME].dt.hour == hour]


st.subheader('Social Distancing Map')


url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
data_topojson_remote = alt.topo_feature(url=url_topojson, feature='counties')
c = alt.Chart(data_topojson_remote).mark_geoshape().properties(width=1000,height = 400)
st.altair_chart(c)



st.subheader("Soziale Distanz über Tage verteilt")
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]

hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"Tag": range(60), "Soziale Distanz": hist})


data2 = pd.DataFrame({"city":["Berlin", "München"],"current":[25,50],"mean":[50,70]})
data2_filtered = data2[data2["city"] == city]

data3 = pd.DataFrame({"city":["Berlin","Berlin","Berlin","Berlin","München", "München"],"date":['10/1/2019','10/2/2019', '10/3/2019', '10/4/2019','10/3/2019', '10/4/2019'],"value":[50,70,80,100,70,80]})
data3_filtered = data3[data3["city"] == city]


if st.checkbox("Show raw data", False):
    st.subheader("Ort gefiltert")
    st.write(data2_filtered)

data3_filtered = data3_filtered.rename(columns={'date':'index'}).set_index('index')


st.line_chart(data3_filtered)