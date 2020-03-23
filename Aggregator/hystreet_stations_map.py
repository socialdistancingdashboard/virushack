import io

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


"""Anzahl der Messstationen :: hystreet"""

@st.cache
def load_data(nrows):
    place1 = pd.read_csv(DATA, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    place1.rename(lowercase, axis="columns", inplace=True)
    return place1

DATA = open('stations_with_ags.csv')

place1 = load_data(1000)


midpoint = (np.average(place1["lat"]), np.average(place1["lon"]))

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 6,
        "pitch":40,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=place1,
            get_position=["lon", "lat"],
            get_color='[0, 220, 0, 0]',
            radius=4000,
            elevation_scale=200,
            elevation_range=[200, 600],
            pickable=True,
            extruded=True,
        ),
    ],
))
