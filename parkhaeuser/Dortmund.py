# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:33:53 2020

@author: Peter
"""

import time
from bs4 import BeautifulSoup
from selenium import webdriver

landkreis = 'Dortmund'
url = 'https://geoweb1.digistadtdo.de/OWSServiceProxy/client/parken.jsp'
sek = 1

def scrape():
    """
    Ermittelt durch HTLM-Parsing die Auslastung der einzelnen Parkhäuser und 
    berechnet anschließend die Auslastung für die ganze Stadt.
    
    Returns
    -------
    data : dict
        Dictionary der Form:
           {'Landkreis': 'Landkreis',
            'Gesamt': 3655,
            'Frei': 3194,
            'Auslastung': 0.12612859097127224,
            'Details': [{'Location': 'location',
                         'Gesamt': 219,
                         'Frei': 208,
                         'Auslastung': 0.0502283105022831},
                        ...]
            }
    """
    
    print(f'Scrape Auslastung der Parkhäuser für {landkreis}')
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(sek)
        response = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        p_list = response.select('#infos')[0].select('dl')
    except Exception as err:
        print(err)
        print(f'Fehler beim Laden der Daten für {landkreis}')
        
    details = []
    total = 0 
    empty = 0
    
    for p in p_list:
        s = p.select('a')
        if s:
            location = s[0].getText()
        else:
            continue
        try:
            plaetze = p.select('.plaetze')[0].select('strong')
            e = int(plaetze[0].getText())
            t = int(plaetze[1].getText())
            """Check ob die Anzahl der Plätze valide ist (Gesamtplätze>=freie Plätze, Gesamtplätze > 0). 
            Der Fall freie Plätze == 0 ist auch nicht valide, da das meinen Beobachtungen nach 
            oft auf ein geschlossenes Parkhaus hinweist.
            """
            if e > t or t <= 0 or not e:
                continue
            o = (t - e) / t
            total += t
            empty += e
            data = {'Location': location,
                    'Gesamt': t,
                    'Frei': e,
                    'Auslastung': o}
            details.append(data)
        except Exception as err:
            print(err)
            print(f'Daten für {landkreis}: {location} nicht gefunden')
            
    if total:
        occupation = (total - empty) / total
        data = {'Landkreis': landkreis,
                'Gesamt': total,
                'Frei': empty,
                'Auslastung': occupation,
                'Details': details}
        print(f'Scrapen der Auslastung der Parkhäuser für {landkreis} erfolgreich')
        return data
    else:
        print(f'Auslastung für {landkreis} kann nicht berechnet werden')
        return None





