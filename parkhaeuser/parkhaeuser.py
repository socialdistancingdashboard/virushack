# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 15:58:56 2020

@author: Peter
"""

import requests
import re
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver


date = datetime.now()


#Köln:
"""Noch nicht alle locations für Köln. Kapazität der Parkhäuser muss noch vervollständigt werden.
Die Daten gibt es hier: https://www.koeln.de/apps/parken/. Vermutlich reicht eine Aufschlüsselung nach den dort
angegebenen Vierteln und nicht für jedes einzelne Parkhaus. 
Unklar ist außerdem der Unterschied zwischen den Gesamt Plätzen/Kurzparker Plätzen.
""" 
locations_co = {'Am Dom': 610,
           'Am Gürzenich': 315,
           'An Farina': 305,
           'Galeria Kaufhof': 1260,
           'Groß Sankt Martin': 145,
           'Hauptbahnhof': 500,
           'Heumarkt': 460 ,
           'Hohe Straße': 280,
           'Maritim': 600,
           'Philharmonie': 390
           }
#fehlende locations: ['REWE', 'Rhein Triadem', 'Rheinauhafen', 'Am Neumarkt', 'Bazaar de Cologne', 'Brückenstraße', 'Cäcilienstraße', 'DuMont-Carré', 'Galeria Karstadt', 'Kreissparkasse', 'Lungengasse', 'Opernpassagen', 'Schildergasse', 'Theater-Parkhaus', 'Wolfsstraße', 'Alte Wallgasse', 'Im Klapperhof', 'Kaiser-Wilhelm-Ring', 'Maastrichter Straße', 'Mediapark', 'Ring Karree', 'Rudolfplatz', 'Sparkasse KölnBonn', 'Köln Arcaden', 'LANXESS arena 1', 'LANXESS arena 2', 'LANXESS arena 4', 'Stadion P2 (P+R)', 'Stadion P1', 'Stadion P3', 'Stadion P4', 'Stadion P6', 'Stadion P7', 'Stadion P8 Bus', 'Stadion P8 Pkw', 'Zoo/Flora', 'Marsdorf/Haus Vorst']
url = 'https://www.stadt-koeln.de/leben-in-koeln/verkehr/parken/parkhaeuser/'

try:
    response_co = requests.get(url)
    response_co.raise_for_status()
    response_co = response_co.text
except Exception as err:
    response_co = None
    print(err)
    print(f'Fehler beim Laden der Website für Köln: {url}')



r = re.compile(r'Freie Plätze">(.*?)<strong><br />(\d*).*?Adresse">(.*?)<br />(.*?)</td>', re.DOTALL)
liste_co = r.findall(response_co)

result_co = {'date': str(date.year)+'-'+str(date.month)+'-'+str(date.day), 
             'time': str(date.hour)+':'+str(date.minute),
             'list': {}}
total_co = 0 
empty_co = 0
for location, empty, adress, plz in liste_co: 
    try:
        total = locations_co[location]
        empty = int(empty)
        occupation = (total - empty) / total
        total_co += total
        empty_co += empty
        result_co['list'][location] = {'adress': adress+','+plz, 'total': total, 'empty': empty, 'occupation': occupation}
    except Exception as err:
        print(err)
        print(f'Kapazität des Parkhauses Köln: {location} nicht bekannt')

if total_co:
    occupation_co = (total_co - empty_co) / total_co
else:
    occupation_co = 0
    print('Auslastung für Köln kann nicht berechnet werden, da keine Daten verfügbar')

result_co['total'] = total_co
result_co['empty'] = empty_co
result_co['occupation'] = occupation_co

with open('parking_cologne_'+str(date.year)+str(date.month)+str(date.day)+'_'+str(date.hour)+str(date.minute)+'.json', 'w') as f:
    s = json.dumps(result_co, indent = 4)
    f.write(s)


#Düsseldorf:
locations_du= ['Altstadt', 'Friedrichstadt', 'Hauptbahnhof', 'Kö', 'Nordstraße', 'Schadowstraße']
url = 'https://vtmanager.duesseldorf.de/info/?parkquartier#main'

"""Scrapen der Website. Da viele JavaScript Elemente, muss der Umweg über webdriver gemacht werden.
   time.sleep(10) muss eventuell für das ausführende System angepasst werden, je nachdem wie lange die Seite lädt.
"""
try:
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(10)
    response_du = str(BeautifulSoup(driver.page_source, 'html.parser'))
    driver.quit()
except Exception as err:
    response_du = None
    print(err)
    print(f'Fehler beim Laden der Website für Düsseldorf: {url}')


"""Mittels regex werden die Belegungszahlen im Quelltext der Seite gesucht und nach Vierteln getrennt in
die JSON Datei geschrieben. Zudem werden die Belegungszahlen für alle Viertel zusammen berechnet und in die
JSON Datei geschrieben.
""" 
result_du = {'date': str(date.year)+'-'+str(date.month)+'-'+str(date.day), 
             'time': str(date.hour)+':'+str(date.minute),
             'list': {}}
total_du = 0 
empty_du = 0
"""Die regex scannt immer für location[...]Belegung[...]nächste location, um zu verhindern, dass die Zahlen falsch
zugeordnet werden, falls die Zahlen für eine location nicht verfügbar sind
"""
for location1, location2 in list(zip(locations_du[0::], locations_du[1::]))+[(locations_du[-1], '')]:
    r = re.compile(r'{}.*?(\d*) von (\d*) frei.*?{}'.format(location1, location2), re.DOTALL)
    try:
        s = r.search(response_du)
        total, empty = int(s.group(2)), int(s.group(1))
        occupation = (total - empty) / total
        result_du['list'][location1] = {'total': total, 'empty': empty, 'occupation': occupation}
        total_du += total
        empty_du += empty
    except Exception as err:
        print(err)
        print(f'Daten für Düsseldorf: {location1} nicht gefunden')

if total_du:
    occupation_du = (total_du - empty_du) / total_du
else:
    occupation_du = 0
    print('Auslastung für Düsseldorf kann nicht berechnet werden, da keine Daten verfügbar')
result_du['total'] = total_du
result_du['empty'] = empty_du
result_du['occupation'] = occupation_du

with open('parking_dusseldorf_'+str(date.year)+str(date.month)+str(date.day)+'_'+str(date.hour)+str(date.minute)+'.json', 'w') as f:
    s = json.dumps(result_du, indent = 4)
    f.write(s)