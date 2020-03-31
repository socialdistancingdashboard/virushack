# Über die Daten
Bei den Datenquellen haben wir uns an bereits öffentlich zugänglichen Daten orientiert, die einen direkten oder mittelbaren Rückschlusss auf Aktivitäten des öffentlichen Lebens erlauben. Weitere Datenquellen sind jederzeit integrierbar und willkommen.


## Daten im Dashboard
### Autoverkehr
**Basis:** [TomTom](https://developer.tomtom.com/)

Basierend auf Daten von TomTom kann die Verkehrsdichte auf den Strassen ausgelesen werden. 
### Menschen an Haltestellen des ÖPNV
**Basis:** [Google Maps](https://maps.google.com)

Google bietet über seinen Dienst Google Maps Transit die Funktion an, zu zeigen, wann ÖPNV Haltestellen wie stark frequentiert sind. Diese Daten haben Philipp auf die Projektidee gebracht und waren die erste Datenquelle.
### Fußgänger in Innenstädten (Laserscanner-Messung) 
**Basis:** [hystreet.com](https://hystreet.com)

hystreet.com misst die Passantenfrequenz innerstädtischer Einzelhandelslagen mit Hilfe von Laserscannern an 117 Standorten in 57 Städten. Hystreet hat uns API-Zugriff gewährt und wir können daher sowohl auf stündlich aktualisierte Zahlen, als auch auf mehrere Jahre zurückliegende Daten zugreifen.
![Hystreet Aufbau](https://i.imgur.com/tasxjUt.jpg)

### Fußgänger auf öffentlichen Webcams
Es gibt viele öffentliche Webcams, die belebte und beliebte Orte in unseren Städten zeigen. Durch Bilderkennungsprozesse werden Menschen auf den Bildern als solche erkannt und gezählt. Die Webcams werden zur Zeit stündlich abgefragt.
![Beispiel Webcamauswertung](https://res.cloudinary.com/devpost/image/fetch/s--kuYyUeyM--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://i.imgur.com/CZmjvDM.jpg)

### Fahrradfahrer 
**Basis:** [Eco-Compteur](https://www.eco-compteur.com/)

In vielen Innenstädten werden Fahrradfahrer an automatisierten Messstellen gezählt und von [Eco-Compteur](https://www.eco-compteur.com/) online gestellt. Die Daten der 42 deutschen Messstellen werden für unseren Datenpool abgerufen. Beispiel: http://eco-public.com/public2/?id=100004595

![Fahradzählstation](https://res.cloudinary.com/devpost/image/fetch/s--icTr_OZZ--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://www.eco-visio.net/Photos/100117707/14315331118971.jpg)

### DB Züge 
**Basis:** [Deutsche Bahn](http://bahn.hafas.de/bin/detect.exe/bin/query.exe/d)
Die Deutsche Bahn bietet ihre Daten zu Zugverbindungen via API an. Diese Daten können herangezogen werden, um z.B. ausgefallene Verbindungen / Halte auszuweisen. Um die Aussagefähigkeit zu unterstreichen anbei ein Beispiel aus Februar:

Im den Diagrammen ist ein Anstieg bei den Zugausfällen am 2020-02-08/09 zu erkennen. Hier hat das Sturmtief Sabrina ganze Arbeit geleistet.
Man sieht in den letzten Tagen einen Anstieg in den Ausfällen bei allen "Zugtypen". Hier kann man von Corona-bedingten Ausfällen ausgehen.
Neben der Gesamtauswahl aller Verbindungen ist es auch möglich nur bestimmte Typen von Verbindungen auswerten zu lassen.
![Auswertung Bahndaten](https://res.cloudinary.com/devpost/image/fetch/s--f7CkxPvI--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://i.imgur.com/8nWEhk5.png)
### ÖPV Busse
Ausgewertet werden mit dieser Auswahl nur die Daten der Deutschen Bahn, die sich auf Busverbindungen beziehen.

### ÖPV IC-Züge
Ausgewertet werden mit dieser Auswahl nur die Daten der Deutschen Bahn, die sich auf Fernverbindungen beziehen, ohne ICE Verbindungen.

### ÖPV Nahverkehr
Ausgewertet werden mit dieser Auswahl nur die Daten der Deutschen Bahn, die sich auf den Nahverkehr beziehen.

### ÖPV Regionalzüge
Ausgewertet werden mit dieser Auswahl nur die Daten für die Regionalzüge aus den Daten der Deutschen Bahn.

### ÖPV ICE-Züge
Mit dieser Auswahl werden die ICE Verbindungen der Deutschen Bahn ausgewertet.

## weitere Daten die schon aggregiert werden
### Lemgo Digital
**Basis:** [Lemgo Digital - Frauenhofer IOSB-INA](https://lemgo-digital.de/index.php/de/)

Diese Daten stammen aus dem Fraunhofer IoT-Reallabor Lemgo Digital. Sie umfassen Passantenfrequenzen sowie Lärm- und Verkehrsdaten an verschiedenen Orten der Stadt. Die Echtzeitdaten werden über entsprechende Sensoren durch das Fraunhofer IOSB-INA selber erfasst und werde in der Urban Data Platform auf Basis von FIWARE verarbeitet. Die Bereitstellung für das Projekt erfolgt als csv-Datei per https Request.

### Parkhäuser
**Basis:** Webseiten von Parkhäusern

Viele Parkhausbetreiber stellen die Auslastungsdaten ihrer Parkhäuser über Webseiten zur Verfügung. Über diese Auslastung lässt sich ebenfalls ablesen, wie frequentiert die Innenstädte noch sind. 

### Luftqualität
**Basis:** [World Air Qwuality Project](https://waqi.info/de/)

Durch die Auswertung von Sensoren für die Luftqualität lassen sich Rückschlüsse auf das Verkehrsaufkommen schliessen. Daher werden auch diese Sensoren für die Erkennung des social distancing genutzt. Wir verwenden die Daten von 402 deutschen Messstationen des World Air Quality Projects und haben so Einblick in Parameter wie die lokale Konzentration von Stickoxiden, Schwefeldioxid, Kohlenstoffmonoxid Feinstaub, Ozon und lokale Wetterdaten (Temperatur, Luftfeuchtigkeit, Luftdruck).

## Aggregation und Datenaufbereitung
Da jede Datenquelle andere Daten bereitstellt und sich die Granularität unterscheidet, werden die Daten aggregiert in einer Datenbank gespeichert. Dabei werden die Geokoordinaten den Landkreisen und Bundesländern zugewiesen. Als zeitliche Aggregation haben wir uns fürs erste auf eine Tagesbasis festgelegt. So liegen die Daten auch in der Datenbank vor. Die aggregierten Daten werden jeweils gegen Referenzdaten des gleichen Wochentags berechnet. Der Score ergibt sich aus der prozentualen Abweichung des aktuellen Wertes im Vergleich zu einem Referenzpunkt. Dabei entsprechen 100% einem normalem Aktivitätsniveau und somit normalem Social Distancing. Kleinere Werte sind ein Indiz für ein gutes Social Distancing, da weniger Menschen unterwegs sind.

## Datenzugriff

Wenn Du als Data Scientist, Datenjournalist oder auch einfach "interessierter Bürger" Zugriff auf die Rohdaten des Dashboards möchtest um Deine eigenen Analysen anzustellen musst Du nicht mal fragen, die Daten kannst Du einfach [hier herunterladen](https://0he6m5aakd.execute-api.eu-central-1.amazonaws.com/prod). Eine API ist in Arbeit.
