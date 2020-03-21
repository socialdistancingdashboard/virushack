#!/usr/bin/env python
# coding: utf-8

# Einkommentieren, falls nur CPU genutzt werden soll

#import os
#os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import numpy as np
import tensorflow.compat.v1 as tf
import cv2
import urllib
from datetime import datetime

# Geklaut von https://gist.github.com/madhawav/1546a4b99c8313f06c0b2d7d7b4a09e2
class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,1]*im_width),
                        int(boxes[0,i,2] * im_height),
                        int(boxes[0,i,3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()



class PeopleCounter:
    def __init__(self, model_path, threshold=0.7):
        self.odapi = DetectorAPI(path_to_ckpt=model_path)
        self.threshold = threshold

    def get_image(self, url):
        resp = urllib.request.urlopen(url)
        self.image = np.asarray(bytearray(resp.read()), dtype="uint8")
        self.image = cv2.imdecode(self.image, -1)

    def count_people(self, verbose=False):
        peoplecount = 0
        boxes, scores, classes, num = self.odapi.processFrame(self.image)
        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > self.threshold:
                box = boxes[i]
                cv2.rectangle(self.image,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)
                peoplecount += 1
            if verbose:
                cv2.imshow('image', self.image)
                cv2.waitKey(0)
        return peoplecount


if __name__ == '__main__':
    model_path = './faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
    webcams = [{'URL':'http://217.24.53.18/record/current.jpg', 'Lat':'50.258318',"Lon":'10.964798','Name':'Coburg Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://www2.annaberg-buchholz.de/webcam/markt.jpg', 'Lat':'50.580062',"Lon":'13.002370','Name':'Annaberg-Buchholz Markt', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.konzil-konstanz.de/webcam/hafen.jpg', 'Lat':'47.660951',"Lon":'9.178256','Name':'Hafen Konstanz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.erfurt.de/webcam/fischmarkt.jpg', 'Lat':'50.978031',"Lon":'11.028691','Name':'Erfurt Fischmarkt', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.juwelier-roller.de/media/webcam/chemnitz_markt.jpg', 'Lat':'50.832587',"Lon":'12.919738','Name':'Chemnitz Markt', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.celle-tourismus.de/webcam/image-640x480.jpg', 'Lat':'52.623973',"Lon":'10.080568','Name':'Celle Stechbahn', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://webcam.heilbronn.de/current.jpg', 'Lat':'49.142365',"Lon":'9.219044','Name':'Heilbronn Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.verkehrsinfos.ulm.de/webcam/einstein/current.jpg', 'Lat':'48.401848',"Lon":'9.992416','Name':'Ulm Olgastrasse', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://achern.de/tools/webcam/webcam/achern-rathaus1.jpg', 'Lat':'48.625454',"Lon":'8.082615','Name':'Achern Rathaus', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://www.marktplatzcam.mybiberach.de/MarktplatzCam000M.jpg', 'Lat':'48.097822',"Lon":'9.787595','Name':'Biberach Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.radolfzell.de/docs/webcam/radolfzell_640.jpg', 'Lat':' 47.745237',"Lon":'8.966910','Name':'Radolfzell Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://ftp.kaufhaus.ludwigbeck.de/webcam/webcam.jpg', 'Lat':'48.137079',"Lon":'11.576006','Name':'München Marienplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://cdn01.koeln.de/uploads/webcam/live.jpg', 'Lat':'50.941278',"Lon":'6.958281','Name':'Köln Domplatte', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://www.adlerauge1.de/subs/www/current.jpg', 'Lat':'51.513989',"Lon":'7.466483','Name':'Dortmund Markt', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.hal-oever.de/webcam/schlastshut.jpg', 'Lat':'53.078206',"Lon":'8.799147','Name':'Bremen Schlachten', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.call-mail-call.de/webcam/000M.jpg', 'Lat':'52.376701',"Lon":'9.728407','Name':'Hannover Laube', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://80.151.116.140:19812/record/current.jpg', 'Lat':'50.043667',"Lon":'10.2330092','Name':'Schweinfurt Spitalstraße', 'Personenzahl':None, 'Stand':None },
               {'URL':'http://109.90.6.242/cgi-bin/faststream.jpg', 'Lat':'52.028423',"Lon":'8.901522','Name':'Lemgo Mittelstraße', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://webcam.bitel.info/webcamgt01/', 'Lat':'51.9064407',"Lon":'8.3782269','Name':'Gütersloh Berliner Platz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.fiwa-forum.de/webcam/fiwa-forum-cam.jpg', 'Lat':'51.630403',"Lon":'13.708284','Name':'Finsterwalde Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://rathaus-hildesheim.de/webcam/webcam.jpg', 'Lat':'52.1527203',"Lon":'9.9515704','Name':'Hildesheim Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.blick.ms/cam-muenster.php','Lat':'51.962064',"Lon":'7.628089', 'Name':'Münster Prinzipalmarkt','Personenzahl':None, 'Stand':None},
               {'URL':'https://www.siegen.de/fileadmin/cms/bilder/Webcam/WebCam_Siegen.jpg', 'Lat':'50.8335211',"Lon":'7.9867985','Name':'Siegen Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://lamp01.dortmund.de/webcams/friedensplatz/current.jpg', 'Lat':'51.511543',"Lon":'7.466345','Name':'Dortmund Friedensplatz', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://lamp01.dortmund.de/webcams/altermarkt_hik/current_TIMING.jpg', 'Lat':'51.513989',"Lon":'7.466483','Name':'Dortmund Alter Markt', 'Personenzahl':None, 'Stand':None },
               {'URL':'https://www.osnabrueck.de/marktplatzwebcam/axis-cgi/mjpg/video.cgi', 'Lat':'52.113777',"Lon":'8.205642','Name':'Osnabrück Marktplatz', 'Personenzahl':None, 'Stand':None }]



    pc = PeopleCounter(model_path)
    for cam in webcams:
        pc.get_image(cam['URL'])
        cam['Personenzahl'] = pc.count_people(verbose=False)
        cam['Stand'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(cam["Name"]+" :"+str(cam["Personenzahl"]))
