TRUNCATE TABLE sdd.categories;
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_fahrrad",
  "Beschreibt das Verhältnis aus gewöhnlichem Radaufkommen und tatsächlichem Radaufkommen in diversen deutschen Städten.",
  "Die Daten sind reichen teilweise bis 2013 zurück.",
  "Nico, Gabriel, Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_all",
  "ÖPV allgemein",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für diverse öffentliche Verkehrsmittel. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_national",
  "ÖPV IC-Züge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Intercity-Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_nationalExpress",
  "ÖPV ICE-Züge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für ICE-Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_regional",
  "ÖPV Regionalzüge",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Regionalzüge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_suburban",
  "ÖPV Nahverkehr",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für innerstädtische Züge. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
INSERT INTO sdd.categories (name, desc_short, desc_long, contributors) 
VALUES(
  "score_public_transportation_bus",
  "ÖPV Busse",
  "Beschreibt das Verhältnis aus tatsächlichen Haltestops und geplanten Haltestops für Busse. Die Daten sind ab 27.02.2020 für alle Gemeinden verfügbar.",
  "Parzival"
);
