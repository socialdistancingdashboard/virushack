# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:33:53 2020

@author: Peter
"""

import time
from bs4 import BeautifulSoup
from selenium import webdriver

"""Template für das Scrapen der Parkhausauslastung eines Landkreises von einer Website.
An den durch Kommentare gekennzeichneten Stellen im Code müssen die CSS-Selektoren für 
Name des Parkhauses usw. eingefügt werden. Eventuell sind noch mehr Anpassungen nötig.
"""

landkreis = ''
url = ''
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
        driver = webdriver.Chrome()
        driver.get(url)
        """Zeit bis alle relevanten Elemente geladen sind, muss je nach Website geändert werden.
        Schöner wäre eine Lösung bei der explizit gewartet wird, bis die Elemente geladen wurden.
        """
        time.sleep(sek)
        response = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        #Parsen der Parkhausliste
        p_list = response.select('')[0]
    except Exception as err:
        print(err)
        print(f'Fehler beim Laden der Daten für {landkreis}')
        
    details = []
    total = 0 
    empty = 0
    for p in p_list:
        try:
            #Parsen des Parkhausnamens
            location = p.select('')[0].getText()
        except Exception:
            continue
        try:
            #Parsen der freien Plätze/Gesamtplätze
            e = int(p.select('')[0].getText())
            t = int(p.select('')[0].getText())
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



