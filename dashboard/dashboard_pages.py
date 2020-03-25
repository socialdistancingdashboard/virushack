import streamlit as st

def about():
    #file = 'https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/README.md'
    st.markdown("""
        <style type='text/css'>
            img {
                max-width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)
    with open('README.md','r') as f:
        st.markdown(f.read())

def impressum():
    st.write('Impressum')
    pass