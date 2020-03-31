Scrapet die Auslastung der Parkhäuser in Landkreisen von verschiedenen Seiten. Danach wird eine JSON-Datei im folgenden Format auf den S3 Bucket geladen.

JSON-Schema:

    [
    {
        "Landkreis": "K\u00f6ln",
        "Gesamt": 3655,
        "Frei": 2278,
        "Auslastung": 0.3767441860465116,
        "Details": [
            {
                "Location": "Am G\u00fcrzenich",
                "Gesamt": 315,
                "Frei": 200,
                "Auslastung": 0.36507936507936506
            },
            (...)
        ]
    },
    {
        "Landkreis": "D\u00fcsseldorf",
        "Gesamt": 7171,
        "Frei": 6471,
        "Auslastung": 0.09761539534235114,
        "Details": [
            (...)
        ]
    },
    {
        "Landkreis": "Frankfurt",
        "Auslastung": 0.12
    },
    {
        "Landkreis": "Wiesbaden",
        "Auslastung": 0.09999999999999998
    },
    {
        "Landkreis": "Mannheim",
        "Auslastung": 0.32999999999999996
    },
    {
        "Landkreis": "Kassel",
        "Auslastung": 0.42000000000000004
    },
    {
        "Landkreis": "Bad Homburg",
        "Auslastung": 0.030000000000000027
    }
]

TODO:    
-weitere Städte hinzufügen  
-evtl alte Daten (vor Corona) finden  
-Scraper von regex auf html-parser umbasteln

Infos und Quellen zu den Daten der einzelnen Städte/Landkreise:  
-Köln:  
-Düsseldorf:  
-Dortmund: https://geoweb1.digistadtdo.de/OWSServiceProxy/client/parken.jsp  (Skript schon erstellt, kommt nachher auf github)
-Frankfurt: https://www.planetradio.de/service/parkhaeuser/  
-Mannheim: https://www.planetradio.de/service/parkhaeuser/  
-Wiesbaden: https://www.planetradio.de/service/parkhaeuser/  
-Kassel: https://www.planetradio.de/service/parkhaeuser/  
-Hochtaunuskreis: https://www.planetradio.de/service/parkhaeuser/ (Es werden nur die Daten für Bad Homburg erhoben)  
-Freiburg: https://www.freiburg.de/pb/,Lde/231355.html#plsmaplink (Die Anzahl der Gesamtplätze wurde händisch in ein dict eingetragen, wird nicht gescrapet. Für das Parkhaus Volksbank ist die Anzahl 0, da das Parkhaus momentan repariert wird. Muss beizeiten angepasst werden. Alternativ ist es auch möglich, die Gesamtzahl zu scrapen, indem nacheinander die Websites für alle Parkhäuser aufgerufen werden. Dafür müsste das Skript angepasst werden)

Bisher noch nicht in den Scraper integriert:  
-Stuttgart: Für Stuttgart sind Daten erst wieder ab Mitte 2020 verfügbar (https://www.stuttgart.de/verkehrslage)  
-Berlin: Bisher keine Website mit Daten gefunden  
-München: Bisher keine Website mit Daten gefunden  
-Hamburg: https://www.hamburg.de/parken/  
-Nürnberg: https://www.tiefbauamt.nuernberg.de/site/parken/parkhausbelegung/parkhaus_belegung.html (Seite funktioniert nicht) ; https://www.parkhaus-nuernberg.de/parkhaeuser/innenstadt/findelgasse.html (nicht alle Parkhäuser)    
-Hannover: https://www.vmz-niedersachsen.de/region-hannover/parkleitsystem-city/  
-Bremen: https://vmz.bremen.de/parken/parkhaeuser-parkplaetze ; https://www.brepark.de/parken/parkhaeuser/ (Die Anzahl der freien Plätze auf beiden Seiten ist gleich, allerdings ist die Auslastung/Gesamtzahl der Plätze unterschiedlich)  
