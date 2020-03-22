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
places.crs = {"init": "epsg:4326"}

print(places)
points_clean = places[places.geometry.type == 'Point']
print(points_clean)


countries = geopandas.GeoDataFrame.from_file("https://raw.githubusercontent.com/AliceWi/TopoJSON-Germany/master/germany.json", layer=1)

countries = countries[["name", "geometry"]]

print(countries)
countries_clean = countries[countries.geometry.type != 'Polygon']
print(countries_clean)

countries.iloc[242]["geometry"].contains(points_clean.iloc[0]["geometry"])

id_grid = geopandas.sjoin(countries_clean,points_clean, how="left", op='intersects')
