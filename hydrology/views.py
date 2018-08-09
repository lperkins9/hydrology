from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import io
from geopandas import datasets, GeoDataFrame, read_file, overlay
from hydrology.functions import zip_to_df
from hydrology.DataFrameFunctions import overlay_hydrology, create_overall_map
from django.utils.encoding import smart_str
import zipfile
from wsgiref.util import FileWrapper

def index(request):
    return render(request, 'index.html')

def gis_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            soils = form.cleaned_data['soils']
            delineationdf = zip_to_df(request.FILES['delineation_file'])
            imperviousdf = zip_to_df(request.FILES['coverage_file'])
            table = overlay_hydrology(delineationdf, imperviousdf, soils)
            overall_map = create_overall_map(delineationdf, imperviousdf)
            
            return render(request, 'gis_results.html', {'table': table[0].to_html(), 'table2': table[1].to_html(), 'table3': table[2].to_html(), 'table4': table[3].to_html()})
        
    else:
        form = UploadFileForm()
    return render(request, 'file_upload_form.html', {'form': form})

def gis_results(request):
    return render(request, 'gis_results.html')

def instructions(request):
    return render(request, 'instructions.html')

def download_csv(request):
    file_path = 'hydrology/output/Drainage_Areas.csv'
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
        
def download_shp(request):
    filenames = ['hydrology/output/Drainage_Areas.cpg','hydrology/output/Drainage_Areas.dbf','hydrology/output/Drainage_Areas.shp','hydrology/output/Drainage_Areas.shx']
    
    zip_subdir = "hydrology/output/"
    zip_filename = "{}/Drainage_Areas.zip".format(zip_subdir)

    response = HttpResponse(content_type='application/zip')
    zip_file = zipfile.ZipFile(response, 'w')
    for filename in filenames:
        zip_file.write(filename)
    response['Content-Disposition'] = 'attachment; filename={}'.format('Drainage_Areas_shp.zip')
    return response