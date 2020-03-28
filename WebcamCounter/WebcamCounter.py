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
import boto3
import json

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
    webcams = [{'ID':1,'URL':'http://217.24.53.18/record/current.jpg', 'Lat':'50.258318',"Lon":'10.964798','Name':'Coburg Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':2,'URL':'http://www2.annaberg-buchholz.de/webcam/markt.jpg', 'Lat':'50.580062',"Lon":'13.002370','Name':'Annaberg-Buchholz Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':3,'URL':'https://www.konzil-konstanz.de/webcam/hafen.jpg', 'Lat':'47.660951',"Lon":'9.178256','Name':'Hafen Konstanz', 'Personenzahl':None, 'Stand':None },
               {'ID':4,'URL':'https://www.erfurt.de/webcam/fischmarkt.jpg', 'Lat':'50.978031',"Lon":'11.028691','Name':'Erfurt Fischmarkt', 'Personenzahl':None, 'Stand':None },
               {'ID':5,'URL':'https://www.juwelier-roller.de/media/webcam/chemnitz_markt.jpg', 'Lat':'50.832587',"Lon":'12.919738','Name':'Chemnitz Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':6,'URL':'https://www.celle-tourismus.de/webcam/image-640x480.jpg', 'Lat':'52.623973',"Lon":'10.080568','Name':'Celle Stechbahn', 'Personenzahl':None, 'Stand':None },
               {'ID':7,'URL':'https://webcam.heilbronn.de/current.jpg', 'Lat':'49.142365',"Lon":'9.219044','Name':'Heilbronn Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':8,'URL':'https://www.verkehrsinfos.ulm.de/webcam/einstein/current.jpg', 'Lat':'48.401848',"Lon":'9.992416','Name':'Ulm Olgastrasse', 'Personenzahl':None, 'Stand':None },
               {'ID':9,'URL':'https://achern.de/tools/webcam/webcam/achern-rathaus1.jpg', 'Lat':'48.625454',"Lon":'8.082615','Name':'Achern Rathaus', 'Personenzahl':None, 'Stand':None },
               {'ID':10,'URL':'http://www.marktplatzcam.mybiberach.de/MarktplatzCam000M.jpg', 'Lat':'48.097822',"Lon":'9.787595','Name':'Biberach Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':11,'URL':'https://www.radolfzell.de/docs/webcam/radolfzell_640.jpg', 'Lat':' 47.745237',"Lon":'8.966910','Name':'Radolfzell Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':12,'URL':'http://ftp.kaufhaus.ludwigbeck.de/webcam/webcam.jpg', 'Lat':'48.137079',"Lon":'11.576006','Name':'München Marienplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':13,'URL':'https://cdn01.koeln.de/uploads/webcam/live.jpg', 'Lat':'50.941278',"Lon":'6.958281','Name':'Köln Domplatte', 'Personenzahl':None, 'Stand':None },
               {'ID':14,'URL':'http://www.adlerauge1.de/subs/www/current.jpg', 'Lat':'51.513989',"Lon":'7.466483','Name':'Dortmund Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':15,'URL':'https://www.hal-oever.de/webcam/schlastshut.jpg', 'Lat':'53.078206',"Lon":'8.799147','Name':'Bremen Schlachten', 'Personenzahl':None, 'Stand':None },
               {'ID':16,'URL':'https://www.call-mail-call.de/webcam/000M.jpg', 'Lat':'52.376701',"Lon":'9.728407','Name':'Hannover Laube', 'Personenzahl':None, 'Stand':None },
               {'ID':17,'URL':'http://80.151.116.140:19812/record/current.jpg', 'Lat':'50.043667',"Lon":'10.2330092','Name':'Schweinfurt Spitalstraße', 'Personenzahl':None, 'Stand':None },
               {'ID':18,'URL':'http://109.90.6.242/record/current.jpg', 'Lat':'52.028423',"Lon":'8.901522','Name':'Lemgo Mittelstraße', 'Personenzahl':None, 'Stand':None },
               {'ID':19,'URL':'https://www.fiwa-forum.de/webcam/fiwa-forum-cam.jpg', 'Lat':'51.630403',"Lon":'13.708284','Name':'Finsterwalde Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':20,'URL':'https://rathaus-hildesheim.de/webcam/webcam.jpg', 'Lat':'52.1527203',"Lon":'9.9515704','Name':'Hildesheim Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':21,'URL':'https://www.siegen.de/fileadmin/cms/bilder/Webcam/WebCam_Siegen.jpg', 'Lat':'50.8335211',"Lon":'7.9867985','Name':'Siegen Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':22,'URL':'https://lamp01.dortmund.de/webcams/friedensplatz/current.jpg', 'Lat':'51.511543',"Lon":'7.466345','Name':'Dortmund Friedensplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':23,'URL':'https://lamp01.dortmund.de/webcams/altermarkt_hik/current_TIMING.jpg', 'Lat':'51.513989',"Lon":'7.466483','Name':'Dortmund Alter Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':24,'URL':'https://service.ka-news.de/tools/webcams/?cam=27', 'Lat':'49.009220',"Lon":'8.403912','Name':'Karlsruhe Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':25,'URL':'https://service.ka-news.de/tools/webcams/?cam=39', 'Lat':'49.0099302',"Lon":'8.3920208','Name':'Karlsruhe Europaplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':26,'URL':'https://www.augsburg.de/fileadmin/user_upload/header/webcam/webcamdachspitz/B_Rathausplatz_Dachspitz_00.jpg', 'Lat':'48.368963',"Lon":'10.898227','Name':'Augsburg Rathausplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':27,'URL':'https://www2.braunschweig.de/webcam/schloss.jpg', 'Lat':'52.263363',"Lon":'10.527763','Name':'Braunschweig Schloss', 'Personenzahl':None, 'Stand':None },
               {'ID':28,'URL':'http://webcambild-rathaus.aachen.de/webcam_rathaus.jpg', 'Lat':'50.776103',"Lon":'6.083780','Name':'Aachen Rathaus', 'Personenzahl':None, 'Stand':None },
               {'ID':29,'URL':'http://www.brillen-krille.de/Webcam/foto.jpg', 'Lat':'54.087890',"Lon":'12.134464','Name':'Rostock Universitätsplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':30,'URL':'https://www.mvv.de/fileadmin/user_upload/Systemdateien/Webcam/current.jpg', 'Lat':'49.4840612',"Lon":'8.4733678','Name':'Mannheim Wasserturm', 'Personenzahl':None, 'Stand':None },
               {'ID':31,'URL':'https://www.theater-schwedt.de/ubs/cam/130/', 'Lat':'53.0617394',"Lon":'14.2838004','Name':'Schwedt Lindenallee', 'Personenzahl':None, 'Stand':None },
               {'ID':32,'URL':'https://webcam.stuttgart.de/wcam007/current.jpg', 'Lat':'48.7754909',"Lon":'9.1763283','Name':'Stuttgart Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':33,'URL':'http://gewerbeverein-adorf.de/Webcam/webcam.jpg', 'Lat':'50.320905',"Lon":'12.2520966','Name':'Adorf Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':34,'URL':'https://www.coswig.de/files/coswig/rathaus/webcam/webcam.jpg', 'Lat':'51.1271276',"Lon":'13.5782501','Name':'Coswig Hauptstrasse', 'Personenzahl':None, 'Stand':None },
               {'ID':35,'URL':'https://ewerk.tv/lvb/LVBHBF/lvbhbf.jpg', 'Lat':'51.3447766',"Lon":'12.379377','Name':'Leipzig Hauptbahnhof', 'Personenzahl':None, 'Stand':None },
               {'ID':35,'URL':'http://www1.mittweida.de/live/current.jpg', 'Lat':'50.9853543',"Lon":'12.9791249','Name':'Mittweida Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':36,'URL':'http://webcam.oelsnitz.de/jpg/image.jpg', 'Lat':'50.4156035',"Lon":'12.1696213','Name':'Oelsnitz Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':37,'URL':'http://www.ku-weit.eu/zittau/Gallery/cam_1.jpg', 'Lat':'50.8962152',"Lon":'14.8080447','Name':'Zittau Salzhaus', 'Personenzahl':None, 'Stand':None },
               {'ID':38,'URL':'https://www.altenburg.eu//WebCam1/axis-cgi/jpg/image.cgi?resolution=640x480', 'Lat':'50.984929',"Lon":'12.4310653','Name':'Altenburg Markt', 'Personenzahl':None, 'Stand':None }, 
               {'ID':39,'URL':'http://wovi95.ddns-instar.com:81/snapshot.jpg?user=gast&pwd=gast&Fri%20Mar%2027%202020%2010%3A15%3A01%20GMT+0100%20%28Mitteleurop%E4ische%20Normalzeit%29', 'Lat':'50.4474983',"Lon":'11.6380773','Name':'Bad Lobenstein Markt', 'Personenzahl':None, 'Stand':None }, 
               {'ID':40,'URL':'https://www.erfurt.de/webcam/domplatz.jpg', 'Lat':'50.9772478',"Lon":'11.0218204','Name':'Erfurt Domplatz', 'Personenzahl':None, 'Stand':None },  
               {'ID':41,'URL':'http://www.thueringer-webcams.de/kunden/mdr/weimar/livebild-pal.jpg', 'Lat':'50.9798182',"Lon":'11.3233716','Name':'Weimar Theaterplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':42,'URL':'http://www.aschersleben.de/webcams/Rathaus.jpeg', 'Lat':'48.6939552',"Lon":'9.1178365','Name':'Aschersleben Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':43,'URL':'https://www.gardelegen.de/webcam/webcam.jpg', 'Lat':'52.446933',"Lon":'11.4835116','Name':'Gardelegen Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':44,'URL':'http://swhcam2.evh.de/vhughsize.jpg', 'Lat':'51.4868011',"Lon":'11.9384423','Name':'Halle (Saale) Markt', 'Personenzahl':None, 'Stand':None },                
               {'ID':45,'URL':'https://webcam.lutherstadt-eisleben.de/markt.jpg', 'Lat':'51.5282306',"Lon":'11.5452827','Name':'Lutherstadt Eisleben Markt', 'Personenzahl':None, 'Stand':None }, 
               {'ID':46,'URL':'http://webcam.naumburg.de/camimage.jpg', 'Lat':'51.152475',"Lon":'11.8073854','Name':'Naumburg (Saale) Markt', 'Personenzahl':None, 'Stand':None },
               {'ID':47,'URL':'https://www.hotelzumbaer.de/cam/image.jpg', 'Lat':'51.789',"Lon":'11.1392834','Name':'Quedlingburg Markt', 'Personenzahl':None, 'Stand':None },  
               {'ID':48,'URL':'https://www.exempel.de/images/webcam/snapshot_current.jpg?', 'Lat':'52.5403281',"Lon":'11.9694902','Name':'Tangermünde Markt', 'Personenzahl':None, 'Stand':None }, 
               {'ID':49,'URL':'https://www.ostseebad-ahrenshoop.de/webcam/ahrenshoop-strand.jpg', 'Lat':'54.3785813',"Lon":'12.4102697','Name':'Ahrenshoop Strand', 'Personenzahl':None, 'Stand':None }, 
               {'ID':50,'URL':'http://www.nwm-net.de/markt/aktuellesbild.jpg', 'Lat':'53.8646453',"Lon":'11.1818843','Name':'Grevesmühlen Markt', 'Personenzahl':None, 'Stand':None },   
               {'ID':51,'URL':'https://media.webdatendienst.de/webcam1_a.jpg', 'Lat':'53.9570837',"Lon":'14.1651142','Name':'Heringsdorf', 'Personenzahl':None, 'Stand':None },
               {'ID':52,'URL':'http://usedomhafen.selfhost.eu:8080/cam_3.jpg', 'Lat':'53.8724447',"Lon":'13.915819','Name':'Usedom', 'Personenzahl':None, 'Stand':None },               
               {'ID':53,'URL':'http://webcam.aichach.de/webaic.jpg', 'Lat':'48.4591603',"Lon":'11.1289321','Name':'Aichach Marktplatz', 'Personenzahl':None, 'Stand':None }, 
               {'ID':54,'URL':'https://mzcam.kunden-mediamachine.de/markt/bild.jpg', 'Lat':'49.9986667',"Lon":'8.2721841','Name':'Mainz Dom', 'Personenzahl':None, 'Stand':None },  
               {'ID':55,'URL':'http://www2.neustadt.eu/download/webcam/current.jpg', 'Lat':'49.3533866',"Lon":'8.1338495','Name':'Neustadt Weinstraße Marktplatz', 'Personenzahl':None, 'Stand':None },   
               {'ID':56,'URL':'https://falken-webcam.worms.de/webcam/current.jpg', 'Lat':'49.6302144',"Lon":'8.3591628','Name':'Worms Marktplatz', 'Personenzahl':None, 'Stand':None }, 
               {'ID':57,'URL':'https://www.bensheim.org/Webcams/images/webcams/current2.jpg', 'Lat':'49.6781939',"Lon":'8.6216948','Name':'Bensheim Fußgängerzone', 'Personenzahl':None, 'Stand':None },
               {'ID':58,'URL':'https://www.bensheim.org/Webcams/images/webcams/current0.jpg', 'Lat':'49.680983',"Lon":'8.6207077','Name':'Bensheim Marktplatz', 'Personenzahl':None, 'Stand':None },               
               {'ID':59,'URL':'http://www.safetec-cam.biz/images/webcam/standard/kaiserstrasse_friedberg.jpg', 'Lat':'50.3347517',"Lon":'8.750523','Name':'Friedberg Kaiserstrasse', 'Personenzahl':None, 'Stand':None },
               {'ID':60,'URL':'http://www.webcam-rimbach.de/images/c1image_big.jpg', 'Lat':'49.623281',"Lon":'8.7570742','Name':'Rimbach Marktplatz', 'Personenzahl':None, 'Stand':None },
               {'ID':61,'URL':'https://www.hal-oever.de/webcam/schlastshut.jpg', 'Lat':'53.0749188',"Lon":'8.8016672','Name':'Bremen Werserpromenande', 'Personenzahl':None, 'Stand':None },
               {'ID':62,'URL':'http://fischmarkt.no-ip.biz/record/current.jpg', 'Lat':'53.5440922',"Lon":'9.9187187','Name':'Hamburg Fischmarkt', 'Personenzahl':None, 'Stand':None },               
               {'ID':63,'URL':'https://www.vvo-online.de/img/webcamimages/marienbruecke-102.jpg', 'Lat':'51.0615957,',"Lon":'13.7320668','Name':'Dresden Marienbrücke', 'Personenzahl':None, 'Stand':None },
               {'ID':64,'URL':'https://www.vvo-online.de/img/webcamimages/koenigsbruecker_strasse_richtung_sued-111.jpg', 'Lat':'51.0700056',"Lon":'13.74682','Name':'Dresden Königsbrücker Str.', 'Personenzahl':None, 'Stand':None },  
               {'ID':65,'URL':'https://www.vvo-online.de/img/webcamimages/albertbruecke-135.jpg', 'Lat':'51.0571946',"Lon":'13.7523692','Name':'Dresden Albertbrücke', 'Personenzahl':None, 'Stand':None },  
               {'ID':66,'URL':'https://www.vvo-online.de/img/webcamimages/bergstrasse-149.jpg', 'Lat':'51.0302823',"Lon":'13.7284321','Name':'Dresden Bergstraße', 'Personenzahl':None, 'Stand':None }, 
               {'ID':67,'URL':'http://allthos.de/lions/dresden.jpg', 'Lat':'51.0564335',"Lon":'13.736906','Name':'Dresden Neustädter Elbufer', 'Personenzahl':None, 'Stand':None },  
               {'ID':68,'URL':'http://webcam.wilhelma.de/webcam02/webcam02.jpg', 'Lat':'48.8041551',"Lon":'9.2058097','Name':'Stuttgart Wilhelma', 'Personenzahl':None, 'Stand':None }]

    pc = PeopleCounter(model_path)

    for cam in webcams:
        try:
            pc.get_image(cam['URL'])
            cam['Personenzahl'] = pc.count_people(verbose=False)
            cam['Stand'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            print(cam["Name"]+" :"+str(cam["Personenzahl"]))
        except:
            pass

    client_s3 = boto3.client("s3" )

    response = client_s3.put_object(
        Bucket="sdd-s3-basebucket",
        Body=json.dumps(webcams),
        Key=f"webcamdaten/{datetime.now().strftime('%Y/%m/%d/%H')}webcamdaten.json"
      )
