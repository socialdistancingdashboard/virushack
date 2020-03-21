""" Dieses Script kann als Vorlage verwendet werden um lon/lat auf Gemeindeschlüssel 
(=ags [amtlicher Gemeindeschlüssel]) zu mappen. 

Ich verwende für die Zuordnung einen nearest-neighbor approach.

install geopy by "pip install geopy"
"""

import pandas as pd
import geopy.distance
import os
import math

# for ipython compatibility
os.chdir(os.path.dirname(__file__))



class GeoToAgs:
  def __init__(self, path_to_csv="data-gemeindeschluessel.csv"):
    self.path = path_to_csv
    # load tab separated values
    self.data = pd.read_csv(path_to_csv, sep="\t")
    # cast to numeric values
    self.data.ags = pd.to_numeric(self.data.ags, errors="coerce")
    self.data.lat = pd.to_numeric(self.data.lat, errors="coerce")
    self.data.lon = pd.to_numeric(self.data.lon, errors="coerce")
    # drop all nan values
    print(len(self.data))
    self.data = self.data[self.data.ags.apply(lambda x: not math.isnan(x))]
    self.data = self.data[self.data.lat.apply(lambda x: not math.isnan(x))]
    self.data = self.data[self.data.lon.apply(lambda x: not math.isnan(x))]
    print(len(self.data))

  
  def distance(self, series):
    #print("hier", series["lat"], series["lon"], self.ref)
    return geopy.distance.vincenty(
      (series["lat"], series["lon"]),
      ref)

  def getAgs(self, ref):
    # TODO: this iterates over all communities. This is not efficient. Data could
    # be sorted to match coords to ags quicker!
    self.ref = ref
    distances = self.data.apply(self.distance, axis=1)
    result = self.data.loc[distances.apply(lambda x: x.m).argmin()]
    return dict(result)
    

# reference point (here: Karlsruhe)
ref = (49.00937, 8.40444)

GTA = GeoToAgs()
result = GTA.getAgs(ref)
# you want to have ags. Explanation for other entries: https://github.com/ratopi/opengeodb/wiki/Amtlicher_Gemeindeschl%25C3%25BCssel
print("Best match is %s which is %s" % (result["ags"], result["ascii"]))
print("all keys:")
print(result)

