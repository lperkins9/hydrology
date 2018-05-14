import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import datasets, GeoDataFrame, read_file, overlay
from numpy import nan
import folium
import os
import pyproj
from selenium import webdriver
import time


def overlay_hydrology(delineationdf, imperviousdf, soils):
    imperviousdf.columns = ['SURFACE_TY','COVERAGE_T','geometry']

    union = overlay(delineationdf,imperviousdf,how='union')
    union.fillna(value=nan, inplace=True)
    union['COVERAGE_T'] = union['COVERAGE_T'].replace([nan],['LAWN'])
    union['SURFACE_TY'] = union['SURFACE_TY'].replace([nan],['PERVIOUS'])
    union['BASIN'] = union['BASIN'].replace([nan],['NOT CAPTURED'])
    union['AREA_SF'] = union['geometry'].area

    table = pd.pivot_table(union, values='AREA_SF', index = ['OUTLET_STR'], columns = ['COVERAGE_T'], aggfunc=np.sum)
    table['SUM'] = table.sum(axis=1)
    table_curve = table
    print(table_curve)

    soils = soils
    cn_table = pd.read_csv('hydrology/cn.csv')

    cn_table.set_index(['COVERAGE'],inplace=True)

    def get_curve_number(row):
        cn_table_list = cn_table.index.tolist()
        row_list = row.index.tolist()
        cn = 0
        for coverage in row_list:
            print(coverage)
            for item in cn_table_list:
                if coverage == item:
                    cn = cn + (row[coverage]*cn_table[soils][item])
        cn = cn/row['SUM']
        print(cn)

        return cn

    curve_table=table_curve.fillna(0)
    print(curve_table)
    curve_table['CN']= curve_table.apply(lambda row: get_curve_number(row), axis=1)
    curve_table.reset_index(level=0,inplace=True)
    curve_table.index.rename('INDEX',inplace=True)

    Drainage_Areas = pd.merge(delineationdf,curve_table,on=['OUTLET_STR'])
    Drainage_Areas.to_file('hydrology/output/Drainage_Areas.shp')
    Drainage_Areas_CSV = Drainage_Areas.drop('geometry',axis=1)
    Drainage_Areas_CSV.to_csv('hydrology/output/Drainage_Areas.csv')
    return Drainage_Areas_CSV.round(decimals=0)

    
#def create_map(union):
#    plot_union = union.dropna()
#    check = []
#    struc = []
#    for item in plot_union['OUTLET_STR']:
#        if item not in check:
#            struc.append(item)
#        check.append(item)
#
#    def convert(x, y):
#        state_plane = pyproj.Proj(init='EPSG:2264', preserve_units=True)
#        wgs = pyproj.Proj(proj='latlong', datum='WGS84', ellps='WGS84')
#        lng, lat = pyproj.transform(state_plane, wgs, x, y)
#        return lat, lng
#
#    union.crs = {'init' :'epsg:2264'}
#    dfx = union.drop(['AREA_SF'],axis=1)
#    delay = 5
#    for structure in struc:    
#        da = dfx[(dfx.OUTLET_STR == structure)]
#        imp = dfx[(dfx.OUTLET_STR == structure) & (dfx.SURFACE_TY == 'IMPERVIOUS')]
#        x_item = delineationdf[(delineationdf.OUTLET_STR == structure)]['geometry'].centroid.x
#        y_item = delineationdf[(delineationdf.OUTLET_STR == structure)]['geometry'].centroid.y
#        point = convert([x_item],[y_item])
#        x = point[0][0]
#        y = point[1][0]
#        mp = folium.Map(location=[x,y], zoom_start = 30, tiles='Stamen Terrain')
#        folium.GeoJson(da, style_function = lambda x :{'fillColor':'green','opacity':100}).add_to(mp)
#        folium.GeoJson(imp, style_function = lambda x :{'fillColor':'black','opacity':0} ).add_to(mp)
#        mp.save(os.path.join('C:/Users/lperkins/Desktop/GIS TEST/', '{}.html'.format(structure)))
#        browser = webdriver.Chrome(executable_path ="C:/Users/lperkins/Desktop/GIS TEST/chromedriver.exe")
#        browser.get('C:/Users/lperkins/Desktop/GIS TEST/'+'{}.html'.format(structure))
#        time.sleep(delay)
#        browser.save_screenshot('C:/Users/lperkins/Desktop/GIS TEST/{}.png'.format(structure))
#        browser.quit()





