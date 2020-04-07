TRUNCATE TABLE sdd.sources;

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "score_lemgodigital_passerby",
  "Passantenfrequenz in Lemgo",
  "Entspricht der Anzahl an Passanten in Lemgo",
  "Fraunhofer IOSB-INA",
  "Anzahl",
  "Anzahl Passanten",
  "Prozent vom Normalwert",
  "daily",
  "avg-percentage-of-normal",
  1
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "score_lemgodigital_traffic",
  "Verkehrsaufkommen in Lemgo",
  "Entspricht der Anzahl an Fahrzeugen in Lemgo",
  "Fraunhofer IOSB-INA",
  "Anzahl",
  "Anzahl Fahrzeuge",
  "Prozent vom Normalwert",
  "daily",
  "avg-percentage-of-normal",
  1
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "score_google_places",
  "Auslastung von ÖPV-Haltestellen",
  "Entspricht der Auslastung von ÖPV-Haltestellen",
  "Google Places",
  "Prozent",
  "Prozent vom Normalwert",
  "Prozent vom Normalwert",
  "hourly",
  "avg-percentage-of-normal",
  1
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "corona_infected",
  "Corona-Infektionen",
  "Entspricht der Anzahl der gemeldeten Corona-Infektionen",
  "Zeit Online",
  "Anzahl",
  "Anzahl Infizierter",
  "Anzahl Infizierter",
  "daily",
  "sum",
  1
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "corona_dead",
  "Corona-Tote",
  "Entspricht der Anzahl der gemeldeten Corona-Toten",
  "Zeit Online",
  "Anzahl",
  "Anzahl Toter",
  "Anzahl Toter",
  "daily",
  "sum",
  1
);

INSERT INTO sdd.sources (id, desc_short, desc_long, contributors, unit, unit_long, unit_agg_long, sample_interval, agg_mode, has_reference_values) 
VALUES(
  "corona_recovered",
  "Gesundete Patienten",
  "Entspricht der (gemeldeten) Anzahl der Patienten, die wieder als gesund entlassen wurden",
  "Zeit Online",
  "Anzahl",
  "Anzahl Gesundeter",
  "Anzahl Gesundeter",
  "daily",
  "sum",
  1
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