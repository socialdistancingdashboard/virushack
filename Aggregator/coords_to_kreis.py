#To run this file you NEED
#pip install Rtree AND
#sudo apt-get update && apt-get install -y libspatialindex-dev OR brew install spatialindex

import geopandas.tools
from shapely.geometry import Point
import pandas as pd

countries = geopandas.GeoDataFrame.from_file(
  "https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json",
  layer=1,
  driver="TopoJSON")
countries
countries = countries[["id", "geometry"]]
countries.columns = ["landkreis_daten", "geometry"]


"""
Converts all lon lat columns in a dataframe into a Series of AGS (Landkreis) Data

:param request: the pandas dataframe
:return: a series of AGS Data
"""

def coords_convert(df):
    def coord_to_point(x):
        return Point(float(x["lon"]), float(x["lat"]))
    df["geometry"] = df.apply(coord_to_point, axis = 1)
    df = geopandas.GeoDataFrame(df, geometry="geometry")
    df = geopandas.sjoin(df, countries, how="left", op='intersects')
    #print(df)
    return df["landkreis_daten"]
    #df.drop(["stopId", "index_right", "geometry"], axis=1, inplace=True)

# Example Usage:

# df["ags"] = coords_convert(pd.DataFrame([{"value": 1,"lat": 48.366512, "lon": 10.894446}])) returns Series Augsburg
