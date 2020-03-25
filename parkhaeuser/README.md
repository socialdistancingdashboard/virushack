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
-Kapazitäten der Parkhäuser in Köln vervollständigen  
-weitere Städte hinzufügen  
-evtl alte Daten (vor Corona) finden
