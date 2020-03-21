# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:18:46 2020

@author: LB


response = requests.get(
    'https://hystreet.com/api/locations/',
    params={},
    headers={'X-API-Token': 'dWfpGRD3aBNocEbZNdLrhRDe'},
)

json_response = response.json()
