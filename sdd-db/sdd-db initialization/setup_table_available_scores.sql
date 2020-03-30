TRUNCATE TABLE sdd.sources;

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_lemgodigital_passerby",
  "Passantenfrequenz in Lemgo",
  "Entspricht der Anzahl an Passanten",
  "Fraunhofer IOSB-INA"
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_lemgodigital_traffic",
  "Verkehrsaufkommen in Lemgo",
  "Entspricht der Anzahl an Fahrzeugen",
  "Fraunhofer IOSB-INA"
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_google_places",
  "Beliebtheit öffentlicher Orte",
  "Entspricht der Auslastung öffentlicher Orte im Vergleich zur gewöhnlichen Auslastung",
  "Google Places"
);



/*
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_google_places",
  "Beliebtheit öffentlicher Orte",
  "Beschreibt die Veränderung der Beliebtheit von öffentlichen Orten durch die Google Places API. Daten liegen sei 22.03.2020 vor.",
  "Todo: add contributors"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_fahrrad",
  "Beschreibt das Verhältnis aus gewöhnlichem Radaufkommen und tatsächlichem Radaufkommen in diversen deutschen Städten.",
  "Die Daten sind reichen teilweise bis 2013 zurück.",
  "Nico, Gabriel, Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_all",
  "ÖPV allgemein",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für diverse öffentliche Verkehrsmittel. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_national",
  "ÖPV IC-Züge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Intercity-Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_nationalExpress",
  "ÖPV ICE-Züge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für ICE-Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_regional",
  "ÖPV Regionalzüge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Regionalzüge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_suburban",
  "ÖPV Nahverkehr",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für innerstädtische Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.sources (id, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_bus",
  "ÖPV Busse",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Busse. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
*/