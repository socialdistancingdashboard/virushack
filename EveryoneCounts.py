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
import urllib
import json
import requests
from PIL import Image
from io import BytesIO

from dashboard import dashboard
from dashboard import dashboard_pages

# sidebar header
response = requests.get('https://github.com/socialdistancingdashboard/virushack/raw/master/logo/logo_with_medium_text.png')
img = Image.open(BytesIO(response.content))
st.sidebar.image(img, use_column_width=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# sidebar menu
menuitems = {'Dashboard':1,'Über das Dashboard':2}#,'Impressum':3}
menu = st.sidebar.radio('',list(menuitems.keys()), index=0)

# hack in some css to style the menu
# note: unsafe_allow_html is planned to be deprecated in future streamlit
# double braces for .format to work
st.markdown("""
    <style type='text/css'>
        div.row-widget.stRadio div[role='radiogroup']>label{{
            background:#FCBFCF;
            margin-bottom:2px;
            padding: 3px 10px 3px 3px;
            width:100%;
        }}
        div.row-widget.stRadio div[role='radiogroup']>label:nth-child({selected}){{
            background:#F63366 !important;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label:nth-child({selected}) *{{
            color:white;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label:hover{{
            background:#F89;
        }}
            div.row-widget.stRadio div[role='radiogroup']>label>div:first-child{{
            display:none;
        }}
    </style>
    """.format(selected=menuitems[menu]), unsafe_allow_html=True)



# main content
if menu=='Dashboard':
    dashboard.dashboard()
elif menu=='Über das Dashboard':
    dashboard_pages.about()
#elif menu=='Impressum':
#    dashboard_pages.impressum()

# sidebar footer
st.sidebar.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.subheader("weitere Infos")
st.sidebar.markdown('''
- [@DistancingDash](https://twitter.com/distancingdash/)
- [Youtube](https://www.youtube.com/watch?v=pDgcbE-c31c&feature=youtu.be)
- [Devpost](https://devpost.com/software/12-social-distancing-dashboard)
''')
