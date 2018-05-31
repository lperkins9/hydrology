import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import datasets, GeoDataFrame, read_file, overlay
from zipfile import ZipFile
import shapefile
import geopandas as gpd
from shapely.geometry import shape  
import osr
import pandas as pd
from io import BytesIO

def zip_to_df(zip_file):
    zipfile = ZipFile(zip_file)
    filenames = [y for y in sorted(zipfile.namelist()) for ending in['dbf','shp','shx','idx', 'cpg'] if y.endswith(ending)]
    cpg, dbf, idx, shp, shx = [BytesIO(zipfile.read(filename)) for filename in filenames]
    r = shapefile.Reader(shp=shp, shx=shx, dbf=dbf, cpg=cpg, idx=idx)
    
    attributes, geometry = [], []
    field_names = [field[0] for field in r.fields[1:]]  
    for row in r.shapeRecords():  
        geometry.append(shape(row.shape.__geo_interface__))  
        attributes.append(dict(zip(field_names, row.record)))
    
    gdf = gpd.GeoDataFrame(data = attributes, geometry = geometry)
    
    return gdf