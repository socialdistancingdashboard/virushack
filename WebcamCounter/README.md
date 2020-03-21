# Webcam Counter
Der Code in diesem Repo stellt ein Modell bereit, um Personen auf Bildern zu zählen. Der Code basiert auf der Object-Detection API von TensorFlow und nutzt ein vortrainiertes Modell. Grundsätzlich sollten alle Modelle aus dem [TensorFlow ModelZoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md#coco-trained-models-coco-models
) funktionieren, getestet und entwickelt wurde aber mit faster_rcnn_inception_v2_coco.

## Funktionsweise
![alt text](https://raw.githubusercontent.com/socialdistancingdashboard/virushack/master/WebcamCounter/Webcam_Example.jpeg "Paxcounter")

Das Skript lädt aktuelle Fotos von derzeit 31 Webcams und speist diese in ein künstliches neuronales Netz zur Objekterkennung ein (Faster RCNN, trainiert auf COCO). Dieses Netzwerk teilt das Foto in verschiedene Bereiche auf, die jeweils ein Objekt enthalten und versucht, die Art des Objekts zu identifizieren. In einem zweiten Schritt durchsucht das Skript das Ergebnis der Objekterkennund nach Objekten vom Typ _Human_ und zählt deren Häufigkeit. Dabei werden nur Bildausschnitte berücksichtigt, bei denen die Sicherheit der Objekterkennung größer als ein vordefinierter Grenzwert (Standard: 60%) ist.

**Wichtig**: Die Objekterkennung funktioniert am besten tagsüber, bei klarer Sicht und trockenem Wetter. Dunkelheit, Regen oder Nebel können die Genauigkeit des Modells deutlich reduzieren oder zum Totalausfall führen.

Das Modell verwendet Code und vortrainierte Modelle von Google TensorFlow.

## Installation
1. Dependencies installieren
```
pip install -r requirements.txt
```
2. Vortrainiertes Modell nach Wahl aus dem [TensorFlow ModelZoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md#coco-trained-models-coco-models
) herunterladen und entpacken.

## Nutzung
Die Datei Webcam_Counter.py kann entweder als eigenständiges Skript ausgeführt werden oder als Modul importiert weden
### Standalone
Im Standalone-Modus iteriert das Skript über eine vorgegebene Liste von Webcams und gibt die Zahl der jeweils gefundenen Personen aus.
Vor dem erstmaligen Ausführen muss unter Umständen der Modellpfad in Zeile 91 angepasst werden:
```python
model_path = './faster_rcnn_inception_v2_coco_XXXX_XX_XX/frozen_inference_graph.pb'
```

### Als Modul
```python
from WebcamCounter import PeopleCounter

model_path = './pfad/zum/modell'
pc = PeopleCounter(model_path)
pc.get_image('http://www.url.de/bild.jpg')
personenzahl = pc.count_people(verbose=False)
print(str(personenzahl)+' Personen wurden erkannt')
```
## Standorte

- Coburg Marktplatz
- Annaberg-Buchholz Markt
- Hafen Konstanz
- Erfurt Fischmarkt
- Chemnitz Markt
- Celle Stechbahn
- Heilbronn Marktplatz
- Ulm Olgastrasse
- Achern Rathaus
- Biberach Marktplatz
- Radolfzell Marktplatz
- München Marienplatz
- Köln Domplatte
- Dortmund Markt
- Bremen Schlachten
- Hannover Laube
- Schweinfurt Spitalstraße
- Lemgo Mittelstraße
- Finsterwalde Marktplatz
- Hildesheim Marktplatz
- Siegen Marktplatz
- Dortmund Friedensplatz
- Dortmund Alter Markt
- Karlsruhe Marktplatz
- Karlsruhe Europaplatz
- Augsburg Rathausplatz
- Braunschweig Schloss
- Aachen Rathaus
- Rostock Universitätsplatz
- Mannheim Wasserturm
- Schwedt Lindenallee


Fragen an: Jochen
