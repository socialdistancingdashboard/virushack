# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:58:56 2020

@author: Peter
"""

import re
import json
import time
from datetime import datetime
import requests
import boto3
from bs4 import BeautifulSoup
from selenium import webdriver


"""Funktionen zum Scrapen des Quelltextes einer Website.

Für Düsseldorf gibt es eine eigene Funktion, da die Website
viele dynamische Elemente besitzt und mit requests.get der
relevante Quelltext für die Belegung der Parkhäuser nicht
erfasst wird. Daher wird der Quelltext mit webdriver und
BeautifulSoup gescrapet. Für die anderen Seiten wird aus
Performancegründen requests verwendet.
"""
def scrape(city, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response = response.text
    except Exception as err:
        response = None
        print(err)
        print(f'Fehler beim Laden der Website für {city} : {url}')
    return response

def scrape_du():
    url = 'https://vtmanager.duesseldorf.de/info/?parkquartier#main'
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        #Sleep, damit alle dynamischen Elemente geladen werden und
        #der komplette Quelltext gescraped wird.
        #Zeit muss eventuell angepasst werden, je nach System.
        time.sleep(10)
        response = str(BeautifulSoup(driver.page_source, 'html.parser'))
        driver.quit()
    except Exception as err:
        response = None
        print(err)
        print(f'Fehler beim Laden der Website für Düsseldorf: {url}')
    return response

def calc_co():
    """Berechnet die Belegung von Köln."""
    url = 'https://www.stadt-koeln.de/leben-in-koeln/verkehr/parken/parkhaeuser/'
    response = scrape('Köln', url)
    r = re.compile(
        r'Freie Plätze">(.*?)<strong><br\s/>(\d*).*?Stellplätze:\s(\d*)',
        re.DOTALL
    )
    liste_co = r.findall(response)

    details = []
    total_co = 0
    empty_co = 0
    for location, empty, total in liste_co:
        try:
            #Sonderfall: für Theather Parkhaus wird total nicht durch
            #die regex abgegriffen
            if location == 'Theater-Parkhaus':
                total = 470
            else:
                total = int(total)
            empty = int(empty)

            #Falls weniger Gesamtplätze als freie Plätze verfügbar sind, liegt
            #offenbar ein Fehler vor (vermutlich ist das Parkhaus geschlossen).
            #Ebenso falls gar keine Parkplätze frei sind (z.B. zu sehen an den
            #Parkplätzen am Stadion).
            if empty > total or total == 0 or not empty:
                continue
            occupation = (total - empty) / total
            total_co += total
            empty_co += empty
            data = {
                'Location': location,
                'Gesamt': total,
                'Frei': empty,
                'Auslastung': occupation}
            details.append(data)
        except Exception as err:
            print(err)
            print(f'Daten für Köln: {location} nicht gefunden')
    if total_co:
        occupation_co = (total_co - empty_co) / total_co
        data = {
            'Landkreis': 'Köln',
            'Gesamt': total_co,
            'Frei': empty_co,
            'Auslastung': occupation_co,
            'Details': details
        }
        return data
    print('Auslastung für Köln kann nicht berechnet werden')
    return None

def calc_du():
    """Berechnet die Belegung von Düsseldorf.

    Mit regex werden die Belegungszahlen im Quelltext der Seite
    gesucht und nach Vierteln getrennt in die JSON Datei geschrieben.
    Zudem werden die Belegungszahlen für alle Viertel zusammen berechnet
    und in die JSON Datei geschrieben.
    """
    locations_du= [
            'Altstadt',
            'Friedrichstadt',
            'Hauptbahnhof',
            'Kö',
            'Nordstraße',
            'Schadowstraße'
        ]
    response = scrape_du()
    total_du = 0
    empty_du = 0
    details = []
    #Die regex scannt immer für location[...]Belegung[...]nächste location,
    #um zu verhindern, dass die Zahlen falsch zugeordnet werden, sollten
    #die Zahlen für eine location nicht verfügbar sein.
    for location1, location2 in list(zip(locations_du[0::], locations_du[1::]))\
                                    +[(locations_du[-1], '')]:
        r = re.compile(
                r'{}.*?(\d*) von (\d*) frei.*?{}'.format(location1, location2),
                re.DOTALL)
        try:
            s = r.search(response)
            total, empty = int(s.group(2)), int(s.group(1))
            occupation = (total - empty) / total
            total_du += total
            empty_du += empty
            data = {
                'Location': location1,
                'Gesamt': total,
                'Frei': empty,
                'Auslastung': occupation
            }
            details.append(data)
        except Exception as err:
            print(err)
            print(f'Daten für Düsseldorf: {location1} nicht gefunden')

    if total_du:
        occupation_du = (total_du - empty_du) / total_du
        data = {
            'Landkreis': 'Düsseldorf',
            'Gesamt': total_du,
            'Frei': empty_du,
            'Auslastung': occupation_du,
            'Details': details}
        return data
    print('Auslastung für Düsseldorf kann nicht berechnet werden'\
          'da keine Daten verfügbar')
    return None

def calc():
    """Berechnet Belegung von mehreren Städten."""
    cities = [
        'Frankfurt',
        'Wiesbaden',
        'Mannheim',
        'Kassel',
        'Bad Homburg'
    ]
    results = []
    response = scrape(
        'Frankfurt',
        'https://www.planetradio.de/service/parkhaeuser/')
    for city in cities:
        try:
            if city == 'Bad Homburg':
                r = re.compile(r'bad-homburg\.html.*?(\d*)\s%', re.DOTALL)
            else:
                r = re.compile(
                    r'{}\.html.*?(\d*)\s%'.format(city.lower()),
                    re.DOTALL)
            s = r.search(response)
            occupation = 1 - (int(s.group(1)) / 100)
            data = {
                'Landkreis': city,
                'Auslastung': occupation
            }
            results.append(data)
        except Exception as err:
            print(err)
            print(f'Daten für {city} nicht gefunden')
    return results

if __name__ == '__main__':
    results = []
    results.append(calc_co())
    results.append(calc_du())
    results.extend(calc())
    if len(results) > 0:
        date = datetime.now()
        s3_client = boto3.client('s3')
        s3_response = s3_client.put_object(
            Body=json.dumps(results),
            Bucket='sdd-s3-basebucket',
            Key=f'parkhaeuser/{str(date.year).zfill(4)}/'\
            '{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/'\
            '{str(date.hour).zfill(2)}'
        )
        print(f'Response: {s3_response}')
