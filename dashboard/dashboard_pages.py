import streamlit as st
import requests

def about():
    response = requests.get('https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/README.md')
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)
    st.markdown(response.text)

def impressum():
    st.write('Impressum')
    pass