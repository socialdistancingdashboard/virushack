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

TODO:    
-Kapazitäten der Parkhäuser in Köln vervollständigen  
-weitere Städte hinzufügen  
-evtl alte Daten (vor Corona) finden
