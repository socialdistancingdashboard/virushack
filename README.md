# EveryoneCounts - Das Social Distancing Dashboard

**[Social Distancing](https://de.wikipedia.org/wiki/R%C3%A4umliche_Distanzierung)** ist eine der wichtigsten Maßnahmen, um die Ausbreitung einer ansteckenden Krankheit zu verlangsamen und letzendlich zu stoppen. Durch unsere Lösung wird Social Distancing jetzt **mess- und anfassbar für alle gesellschaftlichen Stakeholder!**

Die Basis unseres Projektes bildet die kontinuierliche Erfassung und Aufbereitung diverser öffentlich zugänglicher Datenquellen und der anschließenden Aggregation in einem Datenpool. Dieser Datenpool wird auf der einen Seite direkt in einem **[Dashboard](www.everyonecounts.de)** visualisiert um der Gesellschaft auf einfache Weise zu zeigen, wie erfolgreich sich Maßnahmen auf Social Distancing in verschieden Orten und Regionen auswirken. Auf der anderen Seite werden die gesammelten Daten auch der Gesellschaft via **API** zur Verfügung gestellt um die Basis für weitere Anwendungen zu bilden und das Interesse an der Problemstellung weiter zu erhöhen.

[www.everyonecounts.de](https://www.everyonecounts.de)

Du willst uns unterstützen? 
Dann teile: **#EveryoneCounts** 
[Twitter: @DistancingDash #EveryoneCounts](https://twitter.com/DistancingDash)
Like unser [YouTube](https://www.youtube.com/watch?v=pDgcbE-c31c&feature=emb_title) Video.


---


## Was uns antreibt: BürgerInnen, PolitikerInnen und Data Scientists

Die sich momentan in Deutschland exponentiell ausbreitende Corona Epedemie betrifft jedes einzelne Mitglied der Gesellschaft. Daher ergeben sich unterschiedliche Problemstellungen für verschiedene gesellschaftliche Akteure wenn es um die Umsetzung von Maßnahmen geht die das öffentliche Leben beschränken. Im Rahmen unseres MVP's addressieren wir primär BürgerInnen, PolitikerInnen und Data Scientists, wobei zukünftige Weiterentwicklungen auch weitere Stakeholder wie Unternehmen oder andere Länder einschließen werden.

Wir möchten euch folgende Persona's vorstellen: 


![](https://i.imgur.com/9sX8vB2.png)


Björn Bürger - **Bürger** 
Er hält sich an die Vorgaben zum Social Distancing, bleibt zuhause und schaut Fernsehen. Nach zwei Tagen wird ihm das jedoch schon langweilig und er fragt sich:
* "Bringt mein Verhalten überhaupt was?"
* "Halten sich die anderen Bürger*innen auch ans Social Distancing?"
 ---
![](https://i.imgur.com/Gz2IUIK.png)


Reiner Klein - **Bürgermeister einer typischen mittelgroßen Stadt in Deutschland**
In diesen Tagen hat er viele Krisensitzungen zu leiten und sorgt sich um die Gesundheit der Bürger*innen seiner Stadt. Hierbei stellt er sich immer wieder Fragen, wie:
* "Wie wirken die eingeleiteten Maßnahmen? Gibt es Trends?"
* "Muss nachjustiert werden, oder müssen ggf. auch weitergehende Einschränkungen des öffentlichen Lebens beschlossen werden?"

---
![](https://i.imgur.com/Qblf0mY.png)


Franziska Bartels - **engagierte Data Scientistin**
Sie arbeitet momentan im Homeoffice für Ihr Unternehmen und stellt sich die Frage, ob sie neben #wirbleibenzuhause nicht auch noch einen aktiven Beitrag gegen die Ausbreitung von Corona leisten kann. Direkt stellt sich ihr die Frage:
* "Woher bekomme ich die nötigen Daten, um Analysen zu machen oder eine sinnvolle Anwendung zu entwickeln?"

---
## Unsere Vision:

*“Unsere Vision ist es, den Erfolg politischer Maßnahmen zur Reduktion zwischenmenschlicher Interaktionen messbar zu machen um damit einen aktiven Beitrag zur Verlangsamung der Ausbreitung von Corona zu leisten!“*

Hierzu stellen wir allen gesellschaftlichen Akteuren ein **intuitives, datengestütztes Werkzeug** zur Verfügung, mit dem **Social Distancing mess- und anfassbar** wird, ohne sich in der Tiefe mit den Daten auseinandersetzen zu müssen. Um das Ganze so leichtverständlich wie möglich zu gestalten verwenden wir einen relativen **Score**, der das Verhältnis der Aktivitäten an einem bestimmten Wochentag in der Krise zum normalisierten Mittelwert der Aktivitäten an den gleichen Wochentagen vor der Krise, beschreibt. In der aktuellen Implementierung ist der Score ein Wert zwischen 0 und 1, bzw. 0% und 100%. Eine Social Distance von 0 definieren wir als das komplette Ausbleiben einer Änderung der zwischenmenschlichen Interaktion im Vergleich zur üblichen Aktivität vor der Krise, während 1 der maximalen Social Distance, also dem kompletten Nihilierung jeglicher zwischenmenschlichen Interaktion definieren. Die dabei berücksichtigten Datenquellen sind selektierbar. Die nachfolgenden Screenshots zeigen exemplarisch die Funktionalität unserer GUI anhand einer klassichen Click-Journey.

Beim Aufrufen der Website kann der Ort des Interesses eingegeben werden. Durch die farbliche Abstufung sieht man direkt wie effektiv die Social Distancing Maßnahmen momentan im Landkreis und im dazugehörigen Bundesland umgesetzt sind.

![](https://i.imgur.com/jlJ7DUM.png)

Da viele User ein Interesse daran haben zu sehen, wie gut Sie sich selbst im Vergleich zu anderen Nutzern schlagen, ist die Vergleichsmöglichkeit ein wichtiges Feature. Hierbei kann ganz simpel über die Suchmaske ein weitere Ort hinzugefügt werden, was regionale Unterschiede übersichtlich erkennen lässt.

![](https://i.imgur.com/jwepgjT.png)



![](https://i.imgur.com/KEovewX.png)

Um die Wirksamkeit von Maßnahmen zu bewerten, ist es zudem wichtig, den Trend zu sehen. Dazu bietet unsere GUI neben dem tagesaktuellen Score auch die Anzeige historischer Daten an. Für besonders interessierte User können auch noch weitere Datenquellen in einem Dropdown Menü zusätzlich ausgewählt werden, um besonders interessante Zusammenhänge selber analysieren zu können. Momentan angedachte und teilweise bereits implementierte Features sind Wetterdaten des jeweiligen Zeitpunktes, sowie die Anzahl der mit Corona infizierten Menschen, wobei hier die zweiwöchige Inkubationszeit als Timelag herausgerechnet wird.

![](https://i.imgur.com/PxnVcL9.png)

Die Nutzung unserer Daten für die Entwicklung eigener Anwendungen oder die Durchführung von Datenanalysen, unterstützen wir mit einer API. Diese steht bereits zu großen großen Teilen und wird via den zuvorgenannten [Kanälen](https://twitter.com/distancingdash/) veröffentlicht, sowie mit weiteren Datenquellen angereichert werden.

---

## Warum braucht es #EveryoneCounts?

Jede unserer oben beschriebenen Personas hat ihre ganz eigenen Bedürfnisse. Lassen wir doch Björn, Reiner und Franziska sprechen:
![](https://i.imgur.com/p5xkQCe.png)

![](https://i.imgur.com/zHhQTS1.png)

![](https://i.imgur.com/g3VN9K1.png)


Die Anforderungen aller genanngent Stakeholder adressieren wir mit dem Dashboard und der API. Darüberhinaus lassen unsere Datenquellen keine Rückschlüsse auf individuelle Personen zu - anders als beispielsweise bei der Nutzung nachträglich anonymisierter Mobilfunkdaten.

---

## Was haben wir während #WirVsVirus geschafft?
Angefangen hat diese Idee mit Philip's [Twitter](https://www.google.com/url?q=https://twitter.com/pkreissel/status/1239601577759031297&sa=D&ust=1584868096138000&usg=AFQjCNEEL4UN79AXnfizWjNQiqSOeWC6Aw) Post, welcher darauf aufmerksam machen sollte, dass man Social Distancing doch auf Basis von öffentlich zugänglichen Datenquellen quantifizierbar machen könnte. Hierfür hat er im Rahmen des [#WirVsVirus](https://wirvsvirushackathon.org/) Hackathons nach Mitstreitern gesucht um der Idee in kürzester Zeit leben einzuhauchen durch die Einbindung so vieler öffentlich zugänglichen Datenquellen wie möglich. Schnell findet sich ein engagiertes Team für diese komplexe Aufgabe. 

![](https://i.imgur.com/TzXDMhQ.png)

Seit Freitagnacht wurden **7 Datenquellen** identifiziert und integriert, eine **komplette IT- Infrastruktur** entwickelt, ein **[intuitives Frontend](https://www.everyonecounts.de)** aufgebaut, an einer **freien API** gearbeitet und bereits viele **[Datenanalyen](https://twitter.com/DistancingDash)** gefahren.

Eine Menge für 48 Stunden. Zudem wurden während des Hackathons mehrere User Stories erstellt, diese zu Wireframes und Mockups umgewandelt und letzendlich soweit wie möglich in ein responsive Frontend überführt. Dieses [Dashboard](https://www.everyonecounts.de) ist funktionsfähig und stellt einen soliden nutzbaren Startpunkt zur weiteren Entwicklung dar. 

![](https://i.imgur.com/e80Z4Wi.png)
![](https://i.imgur.com/WTQhNNE.png)

Außerdem arbeiten wir mit Hochdruck daran eine API Schnittstelle zur Verfügung zu stellen, um auch Power-Nutzer-innen wie Franziska zufriedenzustellen.

Auch, wenn die Menge der Daten und Quellen in der Zukunft vergrößert werden sollte, ist bereits eine grobe Einschätzung über die Wirksamkeit der Maßnahmen möglich (Erste Analysen finden sich auf [Twitter](https://twitter.com/DistancingDash)).


---

## Wie kann es weiter gehen?
Wie man im Dashboard sehen kann, haben wir es geschafft, ein erstes Dashboard für Björn Bürger zu entwickeln. Leider noch nicht mit der vollen  Funktionalität (bessere Vergleichsfunktion, weitere Daten wie Infektionsraten, Wetter, politische Entscheidungen, historische Daten,...). 

Was gibt es also noch zu tun:
- Bereitstellung einer öffentlichen API
- Dashboard weiterentwicken um die Social-Distancing-Score im Kontext zu präsentieren:
    - Politische Entscheidungen (Schließungen, Verbote, ...)
    - Wetter- und Infektionsdaten
- Intergration von weiteren Datenquellen und [Ideen](https://www.mindmeister.com/de/1444332224?t=GJiE6FEjUm)
- Aggregation finanzieller Unterstützung zur dauerhaften Bereitstellung der API und der zugehörigen Infrastruktur
---
## Technische Dokumentation
Wer an den technischen Raffinessen von *EveryoneCounts - Das Social Distancing Dashboard* interessiert ist, findet unseren Code auf Github: https://github.com/socialdistancingdashboard/virushack/. Außerdem gibt es im folgenden einen knappen Überblick.

### Highlevel Architektur 
![](https://i.imgur.com/EpSzYIx.png)
EveryoneCounts basiert auf einem Datenpool, der sich aus verschiedenen anonymisierten Datensätzen speist. Diese Datensätze werden von speziellen Crawlern abgefragt und als JSON Streams in ein S3 Bucket gespeichert. Von dort werden die Daten per Skript in einer MongoDB aggregiert. Dabei wird auch die Zuordnung der Geokoordinaten zu Landkreisen/Bundesländern gemacht. Im Rahmen des Hackatons haben wir uns darauf verständigt, die Daten jeweils auf Tagesbasis zu aggregieren. Da auch die Daten zum Verlauf der Infektionen auf Tagesbasis ausgewertet werden, ist so eine spätere Korrelation der Werte möglich.

Die Daten werden im Frontend mithilfe des Python-Frameworks [Streamlit](https://www.streamlit.io/) dargestellt.

---

### Datenquellen 
Bei den Datenquellen haben wir uns an bereits öffentlich zugänglichen Daten orientiert, die einen direkten oder mittelbaren Rückschlusss auf Aktivitäten des öffentlichen Lebens erlauben. Weitere Datenquellen sind jederzeit integrierbar und willkommen.

<!--ALT: ![](https://i.imgur.com/xvXVtjQ.png)-->
<!--ALTERNATIV: ![Datenquellen](https://i.imgur.com/QxrA4D3.png)-->
<!--KRAKE: ![Datenquellen](https://i.imgur.com/OS1nni7.png)-->
![Datenquellen](https://i.imgur.com/1nIZu5N.png)

#### hystreet
hystreet.com misst die Passantenfrequenz innerstädtischer Einzelhandelslagen mit Hilfe von Laserscannern an 117 Standorten in 57 Städten. Hystreet hat uns API-Zugriff gewährt und wir können daher sowohl auf stündlich aktualisierte Zahlen, als auch auf mehrere Jahre zurückliegende Daten zugreifen.

#### Eco Compteur
In vielen Innenstädten werden Fahrradfahrer an automatisierten Messstellen gezählt und von [Eco-Compteur](https://www.eco-compteur.com/) online gestellt. Die Daten der 42 deutschen Messstellen werden für unseren Datenpool abgerufen. 
Beispiel: http://eco-public.com/public2/?id=100004595

![Fahradmessstation](https://www.eco-visio.net/Photos/100117707/14315331118971.jpg)


#### Deutsche Bahn
Die Deutsche Bahn bietet ihre Daten zu Zugverbindungen via API an. Diese Daten können herangezogen werden, um z.B. ausgefallene Verbindungen / Halte auszuweisen. Um die Aussagefähigkeit zu unterstreichen anbei ein Beispiel aus Februar:

* Im den Diagrammen ist ein Anstieg bei den Zugausfällen am 2020-02-08/09 zu erkennen. Hier hat das Sturmtief Sabrina ganze Arbeit geleistet.
* Man sieht in den letzten Tagen einen Anstieg in den Ausfällen bei allen "Zugtypen". Hier kann man von Corona-bedingten Ausfällen ausgehen.

![](https://i.imgur.com/8nWEhk5.png)

Mehr Details hier: https://twitter.com/DistancingDash/status/1241730778712678400


#### Google Maps
Google bietet über seinen Dienst Google Maps die Funktion an, zu zeigen, wann bestimmte Orte wie stark frequentiert sind. Diese Daten haben Philipp auf die Projektidee gebracht und waren die erste Datenquelle.

#### Lemgo Digital
Diese Daten stammen aus dem Fraunhofer IoT-Reallabor [Lemgo Digital](https://www.lemgo-digital.de). Sie umfassen Passantenfrequenzen  sowie Lärm- und Verkehrsdaten an verschiedenen Orten der Stadt. Die Echtzeitdaten werden über entsprechende Sensoren durch das Fraunhofer IOSB-INA selber erfasst und werde in der Urban Data Platform auf Basis von FIWARE verarbeitet. Die Bereitstellung für das Projekt erfolgt als csv-Datei per https Request.

![](https://i.imgur.com/tugjMqK.png)

#### World Air Quality Project
Durch die Auswertung von Sensoren für die Luftqualität lassen sich Rückschlüsse auf das Verkehrsaufkommen schliessen. Daher werden auch diese Sensoren für die Erkennung des social distancing genutzt. Wir verwenden die Daten von 402 deutschen Messstationen des [World Air Quality Projects](https://aqicn.org/) und haben so Einblick in Parameter wie die lokale Konzentration von Stickoxiden, Schwefeldioxid, Kohlenstoffmonoxid Feinstaub, Ozon und lokale Wetterdaten (Temperatur, Luftfeuchtigkeit, Luftdruck).

![](https://i.imgur.com/3CHKuWb.png)

#### Öffentliche Webcams
Es gibt viele öffentliche Webcams, die belebte und beliebte Orte in unseren Städten zeigen. Durch Bilderkennungsprozesse werden Menschen auf den Bildern als solche erkannt und gezählt. Die Webcams werden zur Zeit stündlich abgefragt.

![](https://i.imgur.com/CZmjvDM.jpg)

---
### Aggregation und Datenaufbereitung
Da jede Datenquelle andere Daten bereitstellt und sich die Granularität unterscheidet, werden die Daten aggregiert in einer Datenbank gespeichert. Dabei werden die Geokoordinaten den Landkreisen und Bundesländern zugewiesen. Als zeitliche Aggregation haben wir uns fürs erste auf eine Tagesbasis festgelegt. So liegen die Daten auch in der Datenbank vor. Die aggregierten Daten werden jeweils gegen Referenzdaten des gleichen Wochentags berechnet. Der Score berechnet sich aus dem Mittelwert der Berechnung des aktuellen Wertes / den Referenzwert.

---
## API
Wird read only angeboten. Ist noch WIP.


## Unterstützer
Kineo.ai -> Server
Google -> Google Maps API Credits
[Hystreet](http://hystreet.com) -> API
Fraunhofer IOSB-INA -> Daten von Lemgo Digital, Datenaufbereitung, Video
Eco Compteur -> Zugriff auf Fahrradzählstationen

## Publicity

[Tagesspiegel](https://www.tagesspiegel.de/wirtschaft/hackathon-im-netz-programmierer-tuefteln-an-loesungen-gegen-die-corona-krise/25670548.html)

[SWR-Online](https://www.swr.de/swraktuell/wie-deutschland-das-coronavirus-hackt-wirvsvirus-hackathon-100.html)

## Zwischenresultate

Explorative Analyse der Hystreetdaten: https://github.com/socialdistancingdashboard/virushack/blob/master/hystreet/mean_profiles/hystreet_eda.md
Explorative Analyse der Zugdaten: https://github.com/socialdistancingdashboard/virushack/blob/master/zugdaten/README.md
ML Analyse von öffentlichen Webcams zur Ermittlung der Personenanzahl: https://github.com/socialdistancingdashboard/virushack/tree/master/WebcamCounter


Social Distancing Dashboard Team for the WirVsVirusHackathon: https://devpost.com/software/12-social-distancing-dashboard


