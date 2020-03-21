# Peoplecounter
Der Code in diesem Repo stellt ein Modell bereit, um Personen auf Bildern zu zählen. Der Code basiert auf der Object-Detection API von TensorFlow und nutzt ein vortrainiertes Modell. Grundsätzlich sollten alle Modelle aus dem [TensorFlow ModelZoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md#coco-trained-models-coco-models
) funktionieren, getestet und entwickelt wurde aber mit faster_rcnn_inception_v2_coco.

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
## Fragen

Fragen an: Jochen
