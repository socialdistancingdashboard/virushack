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

    #@st.cache()
    def load_real_data(id_to_name):
        response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod')
        jsondump = response.json()["body"]
        
        # get names for all scores
        scorenames = []
        for (date, row) in list(jsondump.items()):
            for cid, scores in row.items():
                for key in scores.keys():
                    if key not in scorenames:
                        scorenames.append(key)
        scorenames = [key for key in scorenames if '_score' in key]
        
        # prepare lists
        scorevalues = {scorename:[] for scorename in scorenames}
        ids = []
        names = []
        dates = []
        
        # loop over data
        for (date, row) in list(jsondump.items()):
            for cid, scores in row.items():
                ids.append(cid)
                names.append(id_to_name[cid])
                dates.append(date)
                for scorename in scorenames:
                    if scorename in scores:
                        scorevalue = scores[scorename]*100
                    else:
                        scorevalue = None
                    scorevalues[scorename].append(scorevalue)
        
        # create dataframe
        df_scores = pd.DataFrame({
            "id": ids, 
            "name": names, 
            "date": dates
        })
        
        # add scores
        for scorename in scorenames:
            df_scores[scorename] = scorevalues[scorename]
        df_scores = df_scores.replace([np.inf, -np.inf], np.nan)
        
        return df_scores, scorenames
    
    # make page here with placeholders
    # thus later elements (e.g. county selector) can influence
    # earlier elements (the map) because they can appear earlier in 
    # the code without appearing earlier in the webpage
    st.title("EveryoneCounts")
    st.header("Das Social Distancing Dashboard")
    st_info_text       = st.empty()
    st_map_header      = st.empty()
    st_map             = st.empty()
    st_timeline_header = st.empty()
    st_county_select   = st.empty()
    st_timeline_desc   = st.empty()
    st_timeline        = st.empty()
    st_footer_title    = st.empty()
    st_footer          = st.empty()
    
    # Insert custom CSS
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 100%;
            }
            div.stVegaLiteChart, fullScreenFrame {
                width:100%;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # get counties
    county_names, county_ids, state_names, state_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    state_id_to_name = {cid:state_names[idx] for idx,cid in enumerate(state_ids)}
    state_name_to_id = {state_names[idx]:cid for idx,cid in enumerate(state_ids)}
    
    # get score data
    df_scores_full, scorenames = load_real_data(id_to_name)
    df_scores = df_scores_full.copy()
    
    # build sidebar
    st.sidebar.subheader("Datenauswahl")
    use_states_select = st.sidebar.selectbox('Detailgrad:', ('Bundesländer', 'Landkreise'))
    use_states = use_states_select == 'Bundesländer'
    
    # descriptive names for each score
    scorenames_desc_manual = {
        "gmap_score":"Besucher an öffentlichen Orten",
        "gmap_supermarket_score":"Besucher in Supermärkten",
        "hystreet_score":"Fußgänger in Innenstädten (Laserscanner-Messung)",
        "zug_score":"DB Züge",
        "bike_score":"Fahradfahrer",
        "bus_score":"ÖPV Busse",
        "national_score":"ÖPV IC-Züge",
        "suburban_score":"ÖPV Nahverkehr",
        "regional_score":"ÖPV Regionalzüge",
        "nationalExpress_score":"ÖPV ICE-Züge",
        "webcam_score":"Fußgänger auf öffentlichen Webcams",
        "tomtom_score":"Autoverkehr"
        }
    # very short axis labels for each score
    scorenames_axis_manual = {
        "gmap_score":"Besucher",
        "gmap_supermarket_score":"Besucher",
        "hystreet_score":"Fußgänger",
        "zug_score":"Züge",
        "bike_score":"Fahradfahrer",
        "bus_score":"Busse",
        "national_score":"IC-Züge",
        "suburban_score":"Nahverkehr",
        "regional_score":"Regionalzüge",
        "nationalExpress_score":"ICE-Züge",
        "webcam_score":"Fußgänger",
        "tomtom_score":"Autoverkehr"
        }
    
    # for scores not in the hardcoded list above
    # default to their scorename as a fallback
    scorenames_desc = {}
    scorenames_axis = {}
    for scorename in scorenames:
        if scorename in scorenames_desc_manual:
            scorenames_desc[scorename] = scorenames_desc_manual[scorename]
        else:
            scorenames_desc[scorename] = scorename
        if scorename in scorenames_axis_manual:
            scorenames_axis[scorename] = scorenames_axis_manual[scorename]
        else:
            scorenames_axis[scorename] = scorename
    inverse_scorenames_desc = {scorenames_desc[key]:key for key in scorenames_desc.keys()}
    
    # data source selector
    selected_score_desc = st.sidebar.selectbox(
        'Datenquelle:', sorted(list(scorenames_desc.values())), 
        index = 1
        )
    selected_score = inverse_scorenames_desc[selected_score_desc]
    selected_score_axis = scorenames_axis[selected_score]
    
    #calculate average score based on selected selected_score
    #if len(selected_score) == 0:
    #    df_scores[selected_score] = df_scores[[scorenames]].mean(axis = 1)
    #elif len(selected_score) == 1:
    #    df_scores[selected_score] = df_scores[[selected_score]]
    #else:
    #    df_scores[selected_score] = df_scores[[selected_score]].mean(axis = 1)

    latest_date = pd.Series(df_scores[df_scores[selected_score] > 0]["date"]).values[-1]

    available_countys = [value for value in county_names if value in df_scores[df_scores[selected_score] > 0]["name"].values]
    if use_states:
        countys = []
    else:
        countys = st_county_select.multiselect('Wähle Landkreise aus:',options = available_countys)

    #selected_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,24))
    #end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))

    #filter scores based on selected places
    if len(countys) > 0:
        df_scores["filtered_score"] = np.where(df_scores["name"].isin(countys), df_scores[selected_score],[0] * len(df_scores))
    else:
        df_scores["filtered_score"] = df_scores[selected_score]

    df_scores["date"] = pd.to_datetime(df_scores["date"])
    df_scores = df_scores.round(1)

    germany_average = np.mean(df_scores[df_scores["date"] == str(latest_date)][selected_score])
    st_info_text.markdown('''
        In der Karte siehst Du wie sich Social Distancing auf die verschiedenen **{regionen}** in Deutschland auswirkt. Wir nutzen Daten über **{datasource}** (Du kannst die Datenquelle links im Menü ändern) um zu berechnen, wie gut Social Distancing aktuell funktioniert. Ein Wert von **100% entspricht dem Normal-Wert vor der Covid-Pandemie**, also bevor die Bürger zu Social Distancing aufgerufen wurden. Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung des Verkehrsaufkommen gemessen wurde, was ein guter Indikator für erfolgreich umgesetztes Social Distancing ist. **Weniger ist besser!**
    '''.format(regionen=use_states_select,datasource=selected_score_desc)
    )
    #st.write("Zum Vergleich - die durchschnittliche Soziale Distanz am {} in Deutschland: {:.2f}".format(latest_date,germany_average))

    st_map_header.subheader('Social Distancing Karte vom {}'.format(latest_date))
    
    if use_states:
        features = 'states'
    else:
        features = 'counties'
    url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    data_topojson_remote = alt.topo_feature(url=url_topojson, feature=features)
    MAPHEIGHT = 600
    basemap = alt.Chart(data_topojson_remote).mark_geoshape(
            fill='lightgray',
            stroke='white'
        ).properties(width='container',height = MAPHEIGHT)
    selected_score_axis_percent = selected_score_axis + ' (%)'
    if use_states:
        # aggregate state data
        df_states = df_scores_full.copy()
        df_states['state_id'] = df_states.apply(lambda x: str(x['id'])[:2],axis=1) # get state id (first two letters of county id)
        df_states['state_name'] = df_states.apply(lambda x: state_id_to_name[x['state_id']],axis=1) # get state name
        df_states = df_states.groupby(['state_name','date']).mean() # group by state and date, calculate mean scores
        df_states = df_states.round(1) #round
        df_states['id'] = df_states.apply(lambda x: state_name_to_id[x.name[0]],axis=1) # re-add state indices
        df_states = df_states.replace([np.inf, -np.inf], np.nan) # remove infs
        df_states = df_states.reset_index() # make index columns into regular columns
        
        #draw state map
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white'
        ).encode(
            color=alt.Color(selected_score+':Q', title=selected_score_axis_percent, scale=alt.Scale(domain=(200, 0),scheme='redyellowgreen')),
            tooltip=[alt.Tooltip("state_name:N", title="Bundesland"),alt.Tooltip(selected_score+":Q", title=selected_score_axis_percent)]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_states[(df_states["date"] == str(latest_date)) & (df_states[selected_score] > 0)], 'id', [selected_score])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_states[(df_states["date"] == str(latest_date)) & (df_states[selected_score] > 0)], 'id', ['state_name'])
        ).properties(width='container',height = MAPHEIGHT)

        c = alt.layer(basemap, layer).configure_view(
            strokeOpacity=0
        )
        st_map.altair_chart(c)
    else:
        # draw counties map
        df_scores_lookup = df_scores[(df_scores["date"] == str(latest_date)) & (df_scores["filtered_score"] > 0)]
        df_scores_lookup = df_scores_lookup[['id','date','name','filtered_score']]
        
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white'
        ).encode(
            color=alt.Color('filtered_score:Q', title=selected_score_axis_percent, scale=alt.Scale(domain=(200, 0),scheme='redyellowgreen')),
            tooltip=[alt.Tooltip("name:N", title="Kreis"),alt.Tooltip("filtered_score:Q", title=selected_score_axis_percent)]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['filtered_score'])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['name'])
        ).properties(width='container',height = MAPHEIGHT)

        c = alt.layer(basemap, layer).configure_view(
            strokeOpacity=0
        )
        st_map.altair_chart(c)

    # draw timelines
    st_timeline_header.subheader("Zeitlicher Verlauf")
    df_scores[df_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()
    if len(countys) > 0 and not use_states:
        
        st_timeline.altair_chart(alt.Chart(
            df_scores[df_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()).mark_line(point=True).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y('filtered_score:Q', title=selected_score_axis_percent),
            color=alt.Color('name', title="Landkreis"),
            tooltip=[
                alt.Tooltip("name:N", title="Landkreis"),
                alt.Tooltip('filtered_score:Q', title=selected_score_axis_percent),
                alt.Tooltip("date:T", title="Datum"),
                ]
        ).properties(
            width='container',
            height=400
        ))
    elif use_states:
        st_timeline.altair_chart(alt.Chart(
            df_states).mark_line(point=True).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y(selected_score+':Q', title=selected_score_axis_percent),
            color=alt.Color('state_name', title="Bundesland", scale=alt.Scale(scheme='category20')),
            tooltip=[
                alt.Tooltip("state_name:N", title="Bundesland"),
                alt.Tooltip(selected_score+":Q", title=selected_score_axis_percent),
                alt.Tooltip("date:T", title="Datum"),
                ]
        ).properties(
            width='container',
            height=400
        ))
    else:
        st_timeline_desc.markdown('''
            Wähle einen oder mehrere Landkreise aus um hier die zeitliche Entwicklung der Daten für {datasource} zu sehen.
        '''.format(datasource=selected_score_desc))
    
    st_footer_title.subheader("Unsere Datenquellen")
    st_footer.markdown("""
        ![](https://github.com/socialdistancingdashboard/virushack/raw/master/logo/Datenquellen.PNG)
    """)
