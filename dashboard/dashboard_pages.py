import streamlit as st
import requests

def about_us():
    response = requests.get('https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/about_us.md')
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 99%;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(response.text, unsafe_allow_html=True)

def about_our_data():
    response = requests.get('https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/about_our_data.md')
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 99%;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(response.text, unsafe_allow_html=True)
    
def about_team():
    response = requests.get('https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/dashboard/das_team.md')
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 99%;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(response.text, unsafe_allow_html=True)

