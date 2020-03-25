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
            county_names.append(county["properties"]["name"] + " (" + county["properties"]["districtType"]+")")
            county_ids.append(county["id"])
        state_names = []
        state_ids = []
        for state in jsondump["objects"]["states"]["geometries"]:
            state_names.append(state["properties"]["name"])
            state_ids.append(state["id"])
        return county_names, county_ids, state_names, state_ids

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

        df_scores = pd.DataFrame(
            {"id": county_ids_prod, "name": county_names_prod, "date": dates_prod, "gmap_score": gmaps_scores_prod, "hystreet_score": hystreet_scores_prod, "zug_score": zug_scores_prod})

        df_scores = df_scores.replace([np.inf, -np.inf], np.nan)

        return df_scores
    
    st.title("#EveryoneCounts - Das Social Distancing Dashboard")
    
    county_names, county_ids, state_names, state_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    state_id_to_name = {cid:state_names[idx] for idx,cid in enumerate(state_ids)}
    state_name_to_id = {state_names[idx]:cid for idx,cid in enumerate(state_ids)}
    
    df_scores_full = load_real_data(county_names, county_ids)
    df_scores = df_scores_full.copy()
    
    st.sidebar.subheader("Datenfilter")
    use_states_select = st.sidebar.selectbox('Detailgrad:', ('Landkreise', 'Bundesländer'))
    use_states = use_states_select == 'Bundesländer'
    
    data_sources_names = {'gmap_score':"Google Popularitätsdaten","hystreet_score":"Fußgänger-Daten (Hystreet)", "zug_score":"Zug-Daten"}
    available_data_sources = [value for value in df_scores.columns if value in data_sources_names.keys()]
    data_sources = st.sidebar.selectbox('Datenquelle:',available_data_sources, format_func=lambda x: data_sources_names[x])

    #calculate average score based on selected data_sources
    if len(data_sources) == 0:
        df_scores["average_score"] = df_scores[[available_data_sources]].mean(axis = 1)
    elif len(data_sources) == 1:
        df_scores["average_score"] = df_scores[[data_sources]]
    else:
        df_scores["average_score"] = df_scores[[data_sources]].mean(axis = 1)

    latest_date = pd.Series(df_scores[df_scores["average_score"] > 0]["date"]).values[-1]

    available_countys = [value for value in county_names if value in df_scores[df_scores["average_score"] > 0]["name"].values]
    if use_states:
        countys = []
    else:
        countys = st.sidebar.multiselect('Wähle Landkreis aus:',options = available_countys)

    #selected_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,24))
    #end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))

    #filter scores based on selected places
    if len(countys) > 0:
        df_scores["filtered_score"] = np.where(df_scores["name"].isin(countys), df_scores["average_score"],[0] * len(df_scores))
    else:
        df_scores["filtered_score"] = df_scores["average_score"]

    df_scores["date"] = pd.to_datetime(df_scores["date"])
    df_scores = df_scores.round(2)

    germany_average = np.mean(df_scores[df_scores["date"] == str(latest_date)]["average_score"])
    st.write("Zum Vergleich - die durchschnittliche Soziale Distanz am {} in Deutschland: {:.2f}".format(latest_date,germany_average))

    st.subheader('Social Distancing Map vom {}'.format(latest_date))
    
    
    if use_states:
        features = 'states'
    else:
        features = 'counties'
    url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    data_topojson_remote = alt.topo_feature(url=url_topojson, feature=features)
    basemap = alt.Chart(data_topojson_remote).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(width=750,height = 1000)
    if use_states:
        # aggregate state data
        df_states = df_scores_full.copy()
        df_states['state_id'] = df_states.apply(lambda x: str(x['id'])[:2],axis=1) # get state id (first two letters of county id)
        df_states['state_name'] = df_states.apply(lambda x: state_id_to_name[x['state_id']],axis=1) # get state name
        df_states = df_states.groupby(['state_name','date']).mean() # group by state and date, calculate mean scores
        df_states = df_states.round(2) #round
        df_states['id'] = df_states.apply(lambda x: state_name_to_id[x.name[0]],axis=1) # re-add state indices
        df_states = df_states.replace([np.inf, -np.inf], np.nan) # remove infs
        df_states = df_states.reset_index() # make index columns into regular columns
        
        #draw state map
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white'
        ).encode(
            color=alt.Color(data_sources+':Q', title="Soziale Distanz", scale=alt.Scale(domain=(2, 0),scheme='redyellowgreen')),
            tooltip=[alt.Tooltip("state_name:N", title="Bundesland"),alt.Tooltip(data_sources+":N", title="Soziale Distanz")]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_states[(df_states["date"] < str(latest_date)) & (df_states[data_sources] > 0)], 'id', [data_sources])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_states, 'id', ['state_name'])
        ).properties(width=750,height = 1000)

        c = alt.layer(basemap, layer).configure_view(
            strokeOpacity=0
        )
        st.altair_chart(c)
    else:
        # draw counties map
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white'
        ).encode(
            color=alt.Color('filtered_score:Q', title="Soziale Distanz", scale=alt.Scale(domain=(2, 0),scheme='redyellowgreen')),
            tooltip=[alt.Tooltip("name:N", title="Kreis"),alt.Tooltip("filtered_score:N", title="Soziale Distanz")]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores[(df_scores["date"] < str(latest_date)) & (df_scores["filtered_score"] > 0)], 'id', ['filtered_score'])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores, 'id', ['name'])
        ).properties(width=750,height = 1000)

        c = alt.layer(basemap, layer).configure_view(
            strokeOpacity=0
        )
        st.altair_chart(c)

    # draw timelines
    df_scores[df_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()
    if len(countys) > 0 and not use_states:
        st.subheader("Zeitlicher Verlauf")
        st.altair_chart(alt.Chart(
            df_scores[df_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()).mark_line(point=True).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y('filtered_score:Q', title="Soziale Distanz"),
            color=alt.Color('name', title="Landkreis")
        ).properties(
            width=750,
            height=400
        ))
    elif use_states:
        st.subheader("Zeitlicher Verlauf")
        st.altair_chart(alt.Chart(
            df_states).mark_line(point=True).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y(data_sources+':Q', title="Soziale Distanz"),
            color=alt.Color('state_name', title="Bundesland", scale=alt.Scale(scheme='category20'))
        ).properties(
            width=750,
            height=400
        ))
    
    st.subheader("Unsere Datenquellen")
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