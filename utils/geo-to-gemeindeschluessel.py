""" Dieses Script kann als Vorlage verwendet werden um lon/lat auf Gemeindeschlüssel 
(=ags [amtlicher Gemeindeschlüssel]) zu mappen. 

Ich verwende für die Zuordnung einen nearest-neighbor approach.

install geopy by "pip install geopy"
@author Parzival
"""

import pandas as pd
import geopy.distance
import os
import math

# for ipython compatibility
os.chdir(os.path.dirname(__file__))



class GeoToAgs:
  """ Class offers functions to map lon/lat to ags (Gemeindeschlüssel)"""
  def __init__(self, path_to_csv="data-gemeindeschluessel.csv"):
    """ Pass the path to csv. This file is contained in the repo, you 
    should just leave it as it is. """
    self.path = path_to_csv
    # load tab separated values
    self.data = pd.read_csv(path_to_csv, sep="\t")
    # cast to numeric values
    self.data.ags = pd.to_numeric(self.data.ags, errors="coerce")
    self.data.lat = pd.to_numeric(self.data.lat, errors="coerce")
    self.data.lon = pd.to_numeric(self.data.lon, errors="coerce")
    # drop all nan values
    self.data = self.data[self.data.ags.apply(lambda x: not math.isnan(x))]
    self.data = self.data[self.data.lat.apply(lambda x: not math.isnan(x))]
    self.data = self.data[self.data.lon.apply(lambda x: not math.isnan(x))]

  
  def distance(self, series):
    # This returns the distance between reference point and each(!) gemeinde
    return geopy.distance.vincenty(
      (series["lat"], series["lon"]),
      ref)

  def getAgs(self, ref):
    # TODO: this iterates over all communities. This is not efficient. Data could
    # be sorted to match coords to ags quicker!
    self.ref = ref
    distances = self.data.apply(self.distance, axis=1)
    result = self.data.loc[distances.apply(lambda x: x.m).argmin()]
    result = dict(result)
    result.update({"distance_in_meters": distances.min().m})
    return result
    

# reference point (here: Karlsruhe)
ref = (49.00937, 8.40444)

GTA = GeoToAgs()
result = GTA.getAgs(ref)
# you want to have ags. Explanation for other entries: https://github.com/ratopi/opengeodb/wiki/Amtlicher_Gemeindeschl%25C3%25BCssel
print("Best match is %s which is %s" % (result["ags"], result["ascii"]))
print("Closest community is %d meters away" % result["distance_in_meters"])
print("\nall keys:")
print(result)

