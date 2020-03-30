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
def load_real_data(dummy_time):
    # dummy_time parameter changes twice daily. Otherwise, streamlit 
    # would always return cached data
    response = requests.get('https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod')
    jsondump = response.json()["body"]
    
    county_names, county_ids, state_names, state_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    
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
    
@st.cache(persist=True)
def get_map(df_scores,selected_score,selected_score_axis,use_states,latest_date):
    url_topojson = 'https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json'
    MAPHEIGHT = 600
    if use_states:
        features = 'states'
        sw = 1
    else:
        features = 'counties'
        sw = 0.2
        # overlay state boundaries with thicker lines
        data_topojson_remote_states = alt.topo_feature(url=url_topojson, feature='states')
        overlaymap = alt.Chart(data_topojson_remote_states).mark_geoshape(
            fill=None,
            stroke='white',
            strokeWidth=1.5
        ).properties(width='container',height = MAPHEIGHT)
    data_topojson_remote = alt.topo_feature(url=url_topojson, feature=features)
   
    basemap = alt.Chart(data_topojson_remote).mark_geoshape(
            fill='lightgray',
            stroke='white',
            strokeWidth=sw
        ).properties(width='container',height = MAPHEIGHT)
    if use_states:
        #draw state map
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white',
            strokeWidth=sw
        ).encode(
                color=alt.Color(selected_score+':Q', 
                                title=selected_score_axis, 
                                scale=alt.Scale(domain=(200, 0),
                                scheme='redyellowgreen'),
                legend=None
            ),
            tooltip=[alt.Tooltip("state_name:N", title="Bundesland"),
                     alt.Tooltip(selected_score+":Q", title=selected_score_axis)]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores[(df_scores["date"] == str(latest_date)) & (df_scores[selected_score] > 0)], 'id', [selected_score])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores[(df_scores["date"] == str(latest_date)) & (df_scores[selected_score] > 0)], 'id', ['state_name'])
        ).properties(width='container',height = MAPHEIGHT)
    else:
        # draw counties map
        df_scores_lookup = df_scores[(df_scores["date"] == str(latest_date)) & (df_scores["filtered_score"] > 0)]
        df_scores_lookup = df_scores_lookup[['id','date','name','filtered_score']]
        
        layer = alt.Chart(data_topojson_remote).mark_geoshape(
            stroke='white',
            strokeWidth=sw
        ).encode(
                color=alt.Color('filtered_score:Q', 
                                title=selected_score_axis, 
                                scale=alt.Scale(domain=(200, 0),
                                scheme='redyellowgreen'),
                legend=None
            ),
            tooltip=[alt.Tooltip("name:N", title="Kreis"),
                     alt.Tooltip("filtered_score:Q", title=selected_score_axis)]
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['filtered_score'])
        ).transform_lookup(
            lookup='id',
            from_= alt.LookupData(df_scores_lookup, 'id', ['name'])
        ).properties(width='container',height = MAPHEIGHT)
    if use_states:
        c = alt.layer(basemap, layer).configure_view(strokeOpacity=0)
    else:
        c = alt.layer(basemap, layer, overlaymap).configure_view(strokeOpacity=0)
    return c
    
@st.cache(persist=True)
def get_timeline_plots(df_scores, selected_score, selected_score_axis, use_states, countys):
    if len(countys) > 0 and not use_states:
        # Landkreise
        df_scores = df_scores[df_scores["name"].isin(countys)].dropna(axis=1, how="all")
        c = alt.Chart(
            df_scores[df_scores["name"].isin(countys)][["name", "date", "filtered_score"]].dropna()
            ).mark_line(point=True).encode(
                x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
                y=alt.Y('filtered_score:Q', title=selected_score_axis),
                color=alt.Color('name', title="Landkreis"),
                tooltip=[
                    alt.Tooltip("name:N", title="Landkreis"),
                    alt.Tooltip('filtered_score:Q', title=selected_score_axis),
                    alt.Tooltip("date:T", title="Datum"),
                    ]
            ).properties(
                width='container',
                height=400
        )
        return c
    elif use_states:
        # Bundesländer
        df_scores=df_scores[["state_name", "date", selected_score]].dropna()
        c = alt.Chart(df_scores).mark_line(point=True).encode(
            x=alt.X('date:T', axis=alt.Axis(title='Datum', format=("%d %b"))),
            y=alt.Y(selected_score+':Q', title=selected_score_axis),
            color=alt.Color('state_name', title="Bundesland", scale=alt.Scale(scheme='category20')),
            tooltip=[
                alt.Tooltip("state_name:N", title="Bundesland"),
                alt.Tooltip(selected_score+":Q", title=selected_score_axis),
                alt.Tooltip("date:T", title="Datum"),
                ]
        ).properties(
            width='container',
            height=400
        )
        return c
    else:
        return None

def detail_score_selector(df_scores_in, scorenames_desc, scorenames_axis, allow_county_select, key, default_detail_index=0, default_score="hystreet_score"):

    df_scores = df_scores_in.copy()
    
    # get counties
    county_names, county_ids, state_names, state_ids = load_topojson()
    id_to_name = {cid:county_names[idx] for idx,cid in enumerate(county_ids)}
    state_id_to_name = {cid:state_names[idx] for idx,cid in enumerate(state_ids)}
    state_name_to_id = {state_names[idx]:cid for idx,cid in enumerate(state_ids)}

    # LEVEL OF DETAIL SELECT
    use_states_select  = st.selectbox('Detailgrad:', 
                                    ('Bundesländer', 'Landkreise'), 
                                    index =default_detail_index,
                                    key = key
                                    )
    use_states = use_states_select == 'Bundesländer'
    
    # SCORE SELECT
    sorted_desc = sorted(list(scorenames_desc.values()))
    selected_score_desc = st.selectbox(
        'Datenquelle:', sorted_desc, 
        index = sorted_desc.index(scorenames_desc[default_score]), # default value in sorted list
        key = key
    )
    inverse_scorenames_desc = {scorenames_desc[key]:key for key in scorenames_desc.keys()}
    selected_score = inverse_scorenames_desc[selected_score_desc]
    selected_score_axis = scorenames_axis[selected_score] + ' (%)'
    
    latest_date = pd.Series(df_scores[df_scores[selected_score] > 0]["date"]).values[-1]
    
    # COUNTY SELECT
    if (not use_states) and allow_county_select:
        available_countys = [value for value in county_names if value in df_scores[df_scores[selected_score] > 0]["name"].values]
        if len(available_countys) > 1:
            default=available_countys[:2]
        else:
            default = []
        countys = st.multiselect('Wähle Landkreise aus:',
                                    options = available_countys, 
                                    default=default,
                                    key = key
                                )
    else:
        countys = []
        
     # Prepare df_scores according to Landkreis/Bundesland selection
    if use_states:
        # aggregate state data
        df_scores['state_id'] = df_scores.apply(lambda x: str(x['id'])[:2],axis=1) # get state id (first two letters of county id)
        df_scores['state_name'] = df_scores.apply(lambda x: state_id_to_name[x['state_id']],axis=1) # get state name
        df_scores = df_scores.groupby(['state_name','date']).mean() # group by state and date, calculate mean scores
        df_scores = df_scores.round(1) #round
        df_scores['id'] = df_scores.apply(lambda x: state_name_to_id[x.name[0]],axis=1) # re-add state indices
        df_scores = df_scores.replace([np.inf, -np.inf], np.nan) # remove infs
        df_scores = df_scores.reset_index() # make index columns into regular columns
    else:
        #filter scores based on selected places
        #if len(countys) > 0:
            #df_scores["filtered_score"] = np.where(df_scores["name"].isin(countys), df_scores[selected_score],[0] *# len(df_scores))
        #else:
        df_scores["filtered_score"] = df_scores[selected_score]

    df_scores["date"] = pd.to_datetime(df_scores["date"])
    df_scores = df_scores.round(1)
    
    return (df_scores,selected_score, selected_score_desc, selected_score_axis, use_states, use_states_select, countys, latest_date)



def dashboard():
    # make page here with placeholders
    # thus later elements (e.g. county selector) can influence
    # earlier elements (the map) because they can appear earlier in 
    # the code without appearing earlier in the webpage
    st.title("EveryoneCounts")
    st.header("Das Social Distancing Dashboard")
    st_map_header      = st.empty()
    st_info_text       = st.empty()
   

    
    # Insert custom CSS
    # - prevent horizontal scrolling on mobile
    # - restrict images to container width
    # - restrict altair plots to container width
    # - make inputs better visible
    st.markdown("""
        <style type='text/css'>
            .block-container>div {
                width:100% !important;
                overflow:hidden !important;
            }
            .image-container {
                width: 99%;
            }
            img {
                max-width: 99%;
                margin:auto;
            }
            div.stVegaLiteChart, fullScreenFrame {
                width:99%;
            }
            .stSelectbox div[data-baseweb="select"]>div,
            .stMultiSelect div[data-baseweb="select"]>div{
                border:1px solid #fcbfcf;
            }
        </style>
    """, unsafe_allow_html=True)
    
    
    # get score data
    dummy_time = datetime.datetime.now().strftime("%Y-%m-%d-%p") # 2020-03-28-PM, changes twice daily
    df_scores_full, scorenames = load_real_data(dummy_time)
    #df_scores = df_scores_full.copy()
    
   
    # descriptive names for each score
    scorenames_desc_manual = {
        "gmap_score":"Menschen an Haltestellen des ÖPNV",
        "gmap_supermarket_score":"Besucher in Supermärkten",
        "hystreet_score":"Fußgänger in Innenstädten (Laserscanner-Messung)",
        "zug_score":"DB Züge",
        "bike_score":"Fahrradfahrer",
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
        "gmap_score":"Menschen",
        "gmap_supermarket_score":"Besucher",
        "hystreet_score":"Fußgänger",
        "zug_score":"Züge",
        "bike_score":"Fahrradfahrer",
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
    
    # Selection box for the map
    df_scores, selected_score, selected_score_desc, selected_score_axis, use_states, use_states_select, countys, latest_date = detail_score_selector(df_scores_full, 
                                        scorenames_desc, 
                                        scorenames_axis, 
                                        allow_county_select=False,
                                        key='map',
                                        default_detail_index=0,
                                        default_score="gmap_score"
                                        )
    st_map             = st.empty()
    st_legend          = st.empty()
    st_timeline_header = st.empty()
    st_timeline_desc   = st.empty()
    
    # Selection box for the timeline
    df_scores2, selected_score2, selected_score_desc2, selected_score_axis2, use_states2, use_states_select2, countys2, latest_date2 = detail_score_selector(df_scores_full, 
                                        scorenames_desc, 
                                        scorenames_axis, 
                                        allow_county_select=True,
                                        key='timeline',
                                        default_detail_index=1,
                                        default_score="hystreet_score"
                                        )

    
    st_timeline        = st.empty()

    #selected_date = st.sidebar.date_input('für den Zeitraum vom', datetime.date(2020,3,24))
    #end_date = st.sidebar.date_input('bis', datetime.date(2020,3,22))


    # WRITE DESCRIPTION TEXTS
    if selected_score == "bike_score"   :
        st_info_text.markdown('''
        In der Karte siehst Du wie sich Social Distancing auf die verschiedenen **{regionen}** in Deutschland auswirkt. Wir nutzen Daten über **{datasource}** um zu berechnen, wie gut Social Distancing aktuell funktioniert. Du kannst die Datenauswahl weiter unten im Menü ändern. Ein Wert von **100% entspricht dem Normal-Wert vor der COVID-Pandemie**, also bevor die Bürger zu Social Distancing aufgerufen wurden. Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung der Aktivität gemessen wurde. **Im Fall von Radfahrern ist ein erhöhtes Verkehrsaufkommen ein positiver Indikator für Social Distancing!** Mehr Menschen sind mit dem Fahrrad unterwegs anstatt mit anderen Verkehrsmitteln, bei denen Social Distancing schwierieger einzuhalten ist.
        '''.format(regionen=use_states_select,datasource=selected_score_desc)
    )
    else:
        st_info_text.markdown('''
        In der Karte siehst Du wie sich Social Distancing auf die verschiedenen **{regionen}** in Deutschland auswirkt. Wir nutzen Daten über **{datasource}** um zu berechnen, wie gut Social Distancing aktuell funktioniert. Du kannst die Datenauswahl weiter unten im Menü ändern. Ein Wert von **100% entspricht dem Normal-Wert vor der COVID-Pandemie**, also bevor die Bürger zu Social Distancing aufgerufen wurden. Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung der Aktivität gemessen wurde, was ein guter Indikator für erfolgreich umgesetztes Social Distancing ist. **Weniger ist besser!**
        '''.format(regionen=use_states_select,datasource=selected_score_desc)
    )
    if selected_score2 == "bike_score"   :
        st_timeline_desc.markdown('''
        Hier kannst du den zeitlichen Verlauf der gewählten Datenquelle für verschiedene **{regionen}** in Deutschland vergleichen. Wir nutzen Daten über **{datasource}** um zu berechnen, wie gut Social Distancing aktuell funktioniert. Du kannst die Datenauswahl weiter unten im Menü ändern. **Ein Wert von 100% entspricht dem Normal-Wert vor der COVID-Pandemie, also bevor die Bürger zu Social Distancing aufgerufen wurden.** Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung der Aktivität gemessen wurde, was ein guter Indikator für erfolgreich umgesetztes Social Distancing ist. **Im Fall von Radfahrern ist ein erhöhtes Verkehrsaufkommen ein positiver Indikator für Social Distancing!** Mehr Menschen sind mit dem Fahrrad unterwegs anstatt mit anderen Verkehrsmitteln, bei denen Social Distancing schwierieger einzuhalten ist.
        
        **Sieh doch mal nach wie die Lage in Deiner Region ist!**
        '''.format(regionen=use_states_select2,datasource=selected_score_desc2)
    )
    else:
        st_timeline_desc.markdown('''
        Hier kannst du den zeitlichen Verlauf der gewählten Datenquelle für verschiedene **{regionen}** in Deutschland vergleichen. Wir nutzen Daten über **{datasource}** um zu berechnen, wie gut Social Distancing aktuell funktioniert. Du kannst die Datenauswahl weiter unten im Menü ändern. **Ein Wert von 100% entspricht dem Normal-Wert vor der COVID-Pandemie, also bevor die Bürger zu Social Distancing aufgerufen wurden.** Ein kleiner Wert weist darauf hin, dass in unserer Datenquelle eine Verringerung der Aktivität gemessen wurde, was ein guter Indikator für erfolgreich umgesetztes Social Distancing ist. 
        
        **Sieh doch mal nach wie die Lage in Deiner Region ist!**
        '''.format(regionen=use_states_select2,datasource=selected_score_desc2)
    )


    try:
        st_map_header.subheader('Social Distancing Karte vom {}'.format( datetime.datetime.strptime(latest_date,"%Y-%m-%d").strftime("%d.%m.%Y") ))
    except:
        st_map_header.subheader('Social Distancing Karte vom {}'.format(latest_date))
    st_legend.image("https://github.com/socialdistancingdashboard/virushack/raw/master/dashboard/legende.png") 
     

   
    # DRAW MAP
    # ========
    map = get_map(df_scores, selected_score, selected_score_axis, use_states, latest_date)
    map2 = map.copy() # otherwise streamlit gives a Cached Object Mutated warning
    st_map.altair_chart(map2)
    
    # DRAW TIMELINES
    # ==============
    st_timeline_header.subheader("Zeitlicher Verlauf")
        
    timeline = get_timeline_plots(df_scores2, selected_score2, selected_score_axis2, use_states2, countys2)
    if timeline is not None:
        timeline2 = timeline.copy() # otherwise streamlit gives a Cached Object Mutated warning
        st_timeline.altair_chart(timeline2)

        
    # FOOTER
    # ======
    st.subheader("Unsere Datenquellen")
    st.markdown("""
        ![](https://github.com/socialdistancingdashboard/virushack/raw/master/logo/Datenquellen.PNG)
    """)
