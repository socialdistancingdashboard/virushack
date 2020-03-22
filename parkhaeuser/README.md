Scrapet die freien Plätze in Parkhäusern von den Seiten der jeweiligen Städte, berechnet die Belegung und schreibt diese in eine JSON-Datei. Das ganze funktioniert durch regex-Suche im Quelltext der jeweiligen Seiten.

JSON-Schema:

    {
        "date": "2020-3-22",    
        "time": "17:28",    
        "list": {    
            "Altstadt": {            
                "total": 2404,            
                "empty": 2241,
                "occupation": 0.06780366056572379
            },
        ...(weitere Viertel)...
        },
        "total": 10914,
        "empty": 9928,
        "occupation": 0.09034267912772585
        }

Requirements:

-Für Düsseldorf: 

from bs4 import BeautifulSoup

from selenium import webdriver
                 
und dazu geckodriver (kann auch zu Chrome geändert werden, falls das besser ist)

TODO:

-parkhaeuser.py vereinfachen, momentan gibt es noch einigen Code mehrfach

-Kapazitäten der Parkhäuser in Köln vervollständigen, nach Stadtvierteln sortieren

-Skript zum Upload der Daten zum AWS server schreiben

-weitere Städte hinzufügen
