from osgeo import gdal, ogr, osr
import os
import datetime
from tqdm import tqdm
import numpy as np

start_time = datetime.datetime.now()

# 定义图片文件类型  
image_types = ('.png')
    
# 遍历输入文件夹中的所有图片文件，并进行处理
img_paths = []
roots = []
img_names = []

folder = r'E:\work\sv_j_ran\20241227\pan2fish\fisheye' #这里就是你的批量栅格存储的文件夹。文件夹里最好除了你的目标栅格数据不要有其他文件了。

for root, dirs, files in os.walk(folder):
    for file in files:
        if file.endswith(image_types):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for i, image_path in enumerate(tqdm(img_paths)): 
    inraster = gdal.Open(image_path)  # 读取路径中的栅格数据
    inband = inraster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1
    
    # 读取栅格数据为numpy数组
    raster_array = inband.ReadAsArray()
    
    # 上下镜像处理
    raster_array = np.flipud(raster_array)
    
    # 将处理后的数组写回到新的栅格文件中
    driver = gdal.GetDriverByName('MEM')  # 使用内存驱动创建临时栅格
    temp_raster = driver.Create('', inraster.RasterXSize, inraster.RasterYSize, 1, inband.DataType)
    temp_raster.SetProjection(inraster.GetProjection())
    temp_raster.SetGeoTransform(inraster.GetGeoTransform())
    temp_band = temp_raster.GetRasterBand(1)
    temp_band.WriteArray(raster_array)
    
    prj = osr.SpatialReference()  
    prj.ImportFromWkt(inraster.GetProjection())   # 读取栅格数据的投影信息，用来为后面生成的矢量做准备
    
    outshp = image_path.replace(r'fisheye', r'fish_shp').replace(r'.png', r'.shp')  # 给后面生成的矢量准备一个输出文件名，这里就是把原栅格的文件名后缀名改成shp了
    folder_path = os.path.dirname(outshp)
    if not os.path.exists(folder_path):
        print(folder_path)
        os.makedirs(folder_path)

    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outshp):  # 若文件已经存在，则删除它继续重新做一遍
        drv.DeleteDataSource(outshp)

    Polygon = drv.CreateDataSource(outshp)  # 创建一个目标文件
    Poly_layer = Polygon.CreateLayer(image_path[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
    newField = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
    Poly_layer.CreateField(newField)

    gdal.FPolygonize(temp_band, None, Poly_layer, 0)  # 核心函数，执行的就是栅格转矢量操作
    Polygon.SyncToDisk() 
    Polygon = None

end_time = datetime.datetime.now()
print("Succeeded at", end_time)
print("Elapsed Time:", end_time - start_time)