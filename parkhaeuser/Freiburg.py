# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:33:53 2020

@author: Peter
"""

import time
from bs4 import BeautifulSoup
from selenium import webdriver

landkreis = 'Freiburg'
url = 'https://www.freiburg.de/pb/,Lde/231355.html'
sek = 10

locations_t = {'Bahnhofsgarage': 219,
               'Konzerthaus': 358,
               'Volksbank': 0,
               'Am Bahnhof': 165,
               'Zur Unterführung': 36,
               'G.-Graf-Halle': 100,
               'Unterlinden': 78,
               'Schwarzwald-City': 421,
               'Rotteck': 300,
               'Zähringer-Tor': 100,
               'Karlsbau': 656,
               'Landratsamt': 206,
               'Schlossberg': 428,
               'Schwabentor': 199,
               'Am Martinstor': 140,
               'Kollegiengebäude': 285}

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
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(sek)
        response = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        p_list = response.select('.pls-nav')[0].select('tr')
    except Exception as err:
        print(err)
        print(f'Fehler beim Laden der Daten für {landkreis}')
        
    details = []
    total = 0 
    empty = 0
    for p in p_list:
        try:
            location = p.select('.pls_col2')[0].select('.pls-links')[0].getText()
        except Exception:
            continue
        try:
            e = int(p.select('.freie_plaetzePls_2')[0].getText())
            t = locations_t[location]
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