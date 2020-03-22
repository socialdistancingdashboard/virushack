import geopandas.tools
import pandas as pd
from shapely.geometry import Point

raw_data = [
    ("Bielefeld", 52.03333, 8.53333),
]

places = pd.DataFrame(raw_data, columns=["name", "latitude", "longitude"])
places["geometry"] = places.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)

del(places["latitude"], places["longitude"])

places = geopandas.GeoDataFrame(places, geometry="geometry")
points_clean = places[places.geometry.type == 'Point']
countries = geopandas.GeoDataFrame.from_file("https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", layer=1)
countries = countries[["name", "geometry"]]

joined_data = geopandas.sjoin(points_clean,countries, how="left", op='intersects')