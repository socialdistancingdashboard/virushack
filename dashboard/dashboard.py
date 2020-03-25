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

def dashboard():
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
            county_names.append(county["properties"]["districtType"]+" - "+county["properties"]["name"])
            county_ids.append(county["id"])

        return county_names, county_ids

    @st.cache(persist=True)
    def load_real_data(county_names, county_ids):

        response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod')

        county_names_prod = []
        county_ids_prod = []
        dates_prod = []
        gmaps_scores_prod = []
        hystreet_scores_prod = []
        zug_scores_prod = []

        data_dict = response.json()["body"]

        for (date, row) in list(data_dict.items()):
            print(date)
            for cid, scores in row.items():
                county_names_prod.append(id_to_name[cid])
                county_ids_prod.append(cid)
                dates_prod.append(date)
                if "gmap_score" in scores:
                    gmaps_scores_prod.append(scores["gmap_score"])
                else:
                    gmaps_scores_prod.append(None)
                if "hystreet_score" in scores:
                    hystreet_scores_prod.append(scores["hystreet_score"])
                else:
                    hystreet_scores_prod.append(None)
                if "zug_score" in scores:
                    zug_scores_prod.append(scores["zug_score"])
                else:
                    zug_scores_prod.append(None)

        df_mock_scores = pd.DataFrame(
            {"id": county_ids_prod, "name": county_names_prod, "date": dates_prod, "gmap_score": gmaps_scores_prod, "hystreet_score": hystreet_scores_prod, "zug_score": zug_scores_prod})

        df_mock_scores = df_mock_scores.replace([np.inf, -np.inf], np.nan)

        return df_mock_scores
    
    st.title("#EveryoneCounts - Das Social Distancing Dashboard")
    
    county_names, county_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    df_mock_scores2 = load_real_data(county_names, county_ids)
    df_mock_scores = df_mock_scores2.copy()

    st.sidebar.subheader("Datenfilter")
    data_sources_names = {'gmap_score':"Google Popularitätsdaten","hystreet_score":"Hystreet Daten", "zug_score":"Zug Daten"}
    available_data_sources = [value for value in df_mock_scores.columns if value in data_sources_names.keys()]
    data_sources = st.sidebar.selectbox('Vergleiche folgende Daten',available_data_sources, format_func=lambda x: data_sources_names[x])

    #calculate average score based on selected data_sources
    if len(data_sources) == 0:
        df_mock_scores["average_score"] = df_mock_scores[[available_data_sources]].mean(axis = 1)
    elif len(data_sources) == 1:
        df_mock_scores["average_score"] = df_mock_scores[[data_sources]]
    else:
        df_mock_scores["average_score"] = df_mock_scores[[data_sources]].mean(axis = 1)

    latest_date = pd.Series(df_mock_scores[df_mock_scores["average_score"] > 0]["date"]).values[-1]

    available_countys = [value for value in county_names if value in df_mock_scores[df_mock_scores["average_score"] > 0]["name"].values]
    countys = st.sidebar.multiselect('für folgende Kreise',options = available_countys)

    #selected_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,24))
    #end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))

    #filter scores based on selected places
    if len(countys) > 0:
        df_mock_scores["filtered_score"] = np.where(df_mock_scores["name"].isin(countys), df_mock_scores["average_score"],[0] * len(df_mock_scores))
    else:
        df_mock_scores["filtered_score"] = df_mock_scores["average_score"]

    df_mock_scores["date"] = pd.to_datetime(df_mock_scores["date"])

    germany_average = np.mean(df_mock_scores[df_mock_scores["date"] == str(latest_date)]["average_score"])
    st.write("Zum Vergleich - die durchschnittliche Soziale Distanz am {} in Deutschland: {:.2f}".format(latest_date,germany_average))

    st.subheader('Social Distancing Map vom {}'.format(latest_date))

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
        tooltip=[alt.Tooltip("name:N", title="Kreis"),alt.Tooltip("filtered_score:N", title="Soziale Distanz")]
    ).transform_lookup(
        lookup='id',
        from_= alt.LookupData(df_mock_scores[(df_mock_scores["date"] == str(latest_date)) & (df_mock_scores["filtered_score"] > 0)], 'id', ['filtered_score'])
    ).transform_lookup(
        lookup='id',
        from_= alt.LookupData(df_mock_scores, 'id', ['name'])
    ).properties(width=750,height = 1000)

    c = alt.layer(basemap, layer).configure_view(
        strokeOpacity=0
    )
    st.altair_chart(c)


    df_mock_scores[df_mock_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()
    if len(countys) > 0:
        st.subheader("Vergleich Soziale Distanz")
        st.altair_chart(alt.Chart(
            df_mock_scores[df_mock_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()).mark_line().encode(
            x=alt.X('date:T', axis=alt.Axis(title='Tag', format=("%d %b"))),
            y=alt.Y('filtered_score:Q', title="Soziale Distanz"),
            color=alt.Color('name', title="Landkreis")
        ).properties(
            width=750,
            height=400
        ))

    response_data_sources = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/Datenquellen.PNG')
    img_data_sources = Image.open(BytesIO(response_data_sources.content))
    st.image(img_data_sources, use_column_width=True)

    st.markdown("""
        <style type='text/css'>
            details {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)