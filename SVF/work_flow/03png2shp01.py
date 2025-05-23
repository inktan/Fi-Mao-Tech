from osgeo import gdal, ogr, osr
import os
import datetime
from tqdm import tqdm
import numpy as np

image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
img_paths = []
roots = []
img_names = []
for root, dirs, files in os.walk(r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_pan_rgb_fisheye_R'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for i,image_path in enumerate(tqdm(img_paths)): 
    # if i<=60000:
    #     continue
    # if i>70000:
    #     continue
    
    outshp = image_path.replace(r'fisheye_R', r'fisheye_shp').replace(r'.png', r'.shp') 
    if os.path.exists(outshp):
        continue
    try:
            
        inraster = gdal.Open(image_path) 
        inband = inraster.GetRasterBand(1) 
        raster_array = inband.ReadAsArray()
        raster_array = np.flipud(raster_array)
        driver = gdal.GetDriverByName('MEM') 
        temp_raster = driver.Create('', inraster.RasterXSize, inraster.RasterYSize, 1, inband.DataType)
        temp_raster.SetProjection(inraster.GetProjection())
        temp_raster.SetGeoTransform(inraster.GetGeoTransform())
        temp_band = temp_raster.GetRasterBand(1)
        temp_band.WriteArray(raster_array)
        
        prj = osr.SpatialReference()  
        prj.ImportFromWkt(inraster.GetProjection()) 
        
        folder_path = os.path.dirname(outshp)
        if not os.path.exists(folder_path):
            # print(folder_path)
            os.makedirs(folder_path)

        drv = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(outshp): 
            drv.DeleteDataSource(outshp)

        Polygon = drv.CreateDataSource(outshp)  
        Poly_layer = Polygon.CreateLayer(image_path[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon) 
        newField = ogr.FieldDefn('value', ogr.OFTReal)  
        Poly_layer.CreateField(newField)

        gdal.FPolygonize(temp_band, None, Poly_layer, 0) 
        Polygon.SyncToDisk() 
        Polygon = None
    except Exception as e:
        print(e)