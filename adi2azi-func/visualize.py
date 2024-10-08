import adif_io as ad
import pandas as pd
import geopandas as gpd
import geodatasets
from shapely.geometry import Point
import matplotlib.pyplot as plt
from PIL import Image


def build_map(bytestream, origin_lat, origin_lon):
    try:
        # read bytestream
        data = bytestream.decode("utf-8")

        qsos_raw, header = ad.read_from_string(data)
        qsos = pd.DataFrame(qsos_raw)

        lolat, lolon = qsos.apply(lambda row : ad.degrees_from_location(row['LAT']), axis=1), qsos.apply(lambda row : ad.degrees_from_location(row['LON']), axis=1)

        # turn into image
        world = gpd.read_file(geodatasets.get_path("naturalearth.land"))
        fig, ax = plt.subplots(figsize = (15,15))

        ax.set_axis_off()
        
        qso_geo = [Point(xy) for xy in zip(lolon, lolat)]
        qso_df = gpd.GeoDataFrame(geometry = qso_geo)
        qso_df.crs = 4326

        origin = [Point(origin_lon, origin_lat)]
        o_df = gpd.GeoDataFrame(geometry = origin)
        o_df.crs = 4326

        trnsfrm_rule = '+proj=laea +lat_0=' + str(origin_lat) + ' +lon_0=' + str(origin_lon) + ' +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs'

        world = world.to_crs(trnsfrm_rule)
        world.plot(ax = ax)

        o_df = o_df.to_crs(trnsfrm_rule)
        origin = o_df.plot(ax = ax, markersize = 30, color = 'yellow', marker = 'o',label = 'You')

        qso_df = qso_df.to_crs(trnsfrm_rule)
        q = qso_df.plot(ax = ax, markersize = 20, color = 'red',marker = 'x',label = 'QSOs')

        fig.canvas.draw()
        buf = fig.canvas.tostring_rgb()
        width, height = fig.canvas.get_width_height()
        image = Image.frombytes("RGB", (width, height), buf)
        return image
    
    except Exception as e:
        return e