# Das Projekt
## Was ist die Idee hinter dem Projekt?
In der Situation mit den weit verbreiteten Regelungen um die Corona Pandemie einzugrenzen, hat sich Philip gefragt, ob man den Erfolg dieser Maßnahmen an öffentlich zugänglichen Daten erkennen kann. Aus dieser Idee und einem eigenen ersten tabellarischen Überblick, auf Basis von Google Places Daten ist das Projekt für den #WirvsVirus - Hackatron entstanden. 
Die Idee hinter dem Dashboard war, für jeden verständlich darzustellen, ob und wie gut das Physical Distancing klappt. Weiterhin soll die breite Datenbasis aufbereitet zur Verfügung gestellt werden, um anderen Interessierten die Möglichkeit zu geben, eigene Auswertungen anzustellen.

## Für wen tun wir das? 
Im Rahmen des Hackatrons wurde die Idee verfeinert und für drei Gruppen von Anwendern ausgearbeitet.

### Björn Bürger - Bürger
![Björn Bürger](https://res.cloudinary.com/devpost/image/fetch/s--UpjqVSef--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://i.imgur.com/9sX8vB2.png)
Er hält sich an die Vorgaben zum Physical Distancing, bleibt zuhause und schaut Fernsehen. Nach zwei Tagen wird ihm das jedoch schon langweilig und er fragt sich:
#### Fragestellungen:
- "Bringt mein Verhalten überhaupt was?"
- "Halten sich die anderen Bürger*innen auch ans Physical Distancing?"

#### Anforderungen:
- Einfache, schnelle Übersicht über Physical Distancing bekommen ohne raus zu gehen (auf einen Blick)
- Vergleichen zwischen verschiedenen Örtlichkeiten
- Teilen um Freunde darauf aufmerksam zu machen

----

### Reiner Klein - Bürgermeister einer typischen mittelgroßen Stadt in Deutschland
![Reiner Klein](https://res.cloudinary.com/devpost/image/fetch/s--E_83r2tv--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://i.imgur.com/Gz2IUIK.png)
In diesen Tagen hat er viele Krisensitzungen zu leiten und sorgt sich um die Gesundheit der Bürger*innen seiner Stadt. 

#### Fragestellungen:
- "Wie wirken die eingeleiteten Maßnahmen? Gibt es Trends?"
- "Muss nachjustiert werden, oder müssen ggf. auch weitergehende Einschränkungen des öffentlichen Lebens beschlossen werden?"
- "Wie können wir aus Covid-19 für die Zukunft lernen?"

#### Anfoderungen:
- Übersicht über die Effektivität seiner Maßnahmen
- Entscheidungsgrundlage für weitere Schutzmaßnahmen

----
### Franziska Bartels - engagierte Data Scientistin
![Fanzsika Bartels](https://res.cloudinary.com/devpost/image/fetch/s--8GuvK94n--/c_limit,f_auto,fl_lossy,q_auto:eco,w_900/https://i.imgur.com/Qblf0mY.png)
ie arbeitet momentan im Homeoffice für Ihr Unternehmen und stellt sich die Frage, ob sie neben #wirbleibenzuhause nicht auch noch einen aktiven Beitrag gegen die Ausbreitung von Corona leisten kann. Direkt stellt sich ihr die Frage:

#### Fragestellungen:
- "Woher bekomme ich die nötigen Daten, um Analysen zu machen oder eine sinnvolle Anwendung zu entwickeln?"

#### Anforderungen:
- Möchte schnell viele Datenquellen vergleichen
- Hat keine Zeit die verschiedenen Quellen selber zu crawlen
----

## Unsere Vision
“Unsere Vision ist es, den Erfolg politischer Maßnahmen zur Reduktion zwischenmenschlicher Interaktionen messbar zu machen um damit einen aktiven Beitrag zur Verlangsamung der Ausbreitung von Corona zu leisten!“

Hierzu stellen wir **allen gesellschaftlichen Akteuren** ein **intuitives, datengestütztes Werkzeug** zur Verfügung, mit dem Physical Distancing mess- und anfassbar wird, ohne sich in der Tiefe mit den Daten auseinandersetzen zu müssen. Um das Ganze so leichtverständlich wie möglich zu gestalten verwenden wir einen relativen Score, der das Verhältnis der Aktivitäten an einem bestimmten Wochentag in der Krise zum normalisierten Mittelwert der Aktivitäten an den gleichen Wochentagen vor der Krise, beschreibt. In der aktuellen Implementierung ist der Score ein Wert zwischen 0 und 1, bzw. 0% und 100%. Eine Physical Distance von 0 definieren wir als das komplette Ausbleiben einer zwischenmenschlichen Interaktion im Vergleich zur üblichen Aktivität vor der Krise, während 1 der üblichen Physical Distance an einem Ort entspricht. Die dabei berücksichtigten Datenquellen sind selektierbar.

Um die Wirksamkeit von Maßnahmen zu bewerten, ist es zudem wichtig, den Trend zu sehen. Dazu bietet unsere GUI neben dem tagesaktuellen Score auch die Anzeige historischer Daten an. Für besonders interessierte User können weitere Datenquellen in einem Dropdown Menü ausgewählt werden, um relevante Zusammenhänge selber analysieren zu können. Momentan angedachte und teilweise bereits implementierte Features sind Wetterdaten des jeweiligen Zeitpunktes, sowie die Anzahl der mit Corona infizierten Menschen, wobei hier die zweiwöchige Inkubationszeit als Timelag herausgerechnet wird.

