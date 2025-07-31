from osgeo import gdal, ogr, osr
import os
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import traceback

# 全局变量，避免在多进程中出现GDAL驱动程序问题
gdal.UseExceptions()
ogr.UseExceptions()

def process_image_to_shp(args):
    """
    将单个图像转换为Shapefile
    :param args: (image_path, overwrite)
    :return: (成功返回None, 失败返回错误信息和文件路径)
    """
    image_path, overwrite = args
    outshp = image_path.replace('半球_fisheye_01', 'fisheye_shp').replace('.png', '.shp').replace('.jpg', '.shp').replace('.jpeg', '.shp')
    
    if not overwrite and os.path.exists(outshp):
        return None
    
    try:
        # 打开原始图像
        inraster = gdal.Open(image_path)
        if inraster is None:
            raise ValueError(f"无法打开图像文件: {image_path}")
        
        inband = inraster.GetRasterBand(1)
        raster_array = inband.ReadAsArray()
        raster_array = np.flipud(raster_array)
        
        # 创建临时内存栅格
        driver = gdal.GetDriverByName('MEM')
        temp_raster = driver.Create('', inraster.RasterXSize, inraster.RasterYSize, 1, inband.DataType)
        temp_raster.SetProjection(inraster.GetProjection())
        temp_raster.SetGeoTransform(inraster.GetGeoTransform())
        temp_band = temp_raster.GetRasterBand(1)
        temp_band.WriteArray(raster_array)
        
        # 设置空间参考
        prj = osr.SpatialReference()
        prj.ImportFromWkt(inraster.GetProjection())
        
        # 创建输出目录
        folder_path = os.path.dirname(outshp)
        os.makedirs(folder_path, exist_ok=True)
        
        # 创建Shapefile
        drv = ogr.GetDriverByName("ESRI Shapefile")
        if os.path.exists(outshp):
            drv.DeleteDataSource(outshp)
        
        Polygon = drv.CreateDataSource(outshp)
        Poly_layer = Polygon.CreateLayer(os.path.basename(image_path)[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)
        newField = ogr.FieldDefn('value', ogr.OFTReal)
        Poly_layer.CreateField(newField)
        
        # 执行多边形化
        gdal.FPolygonize(temp_band, None, Poly_layer, 0)
        Polygon.SyncToDisk()
        Polygon = None
        
        return None
    except Exception as e:
        return (image_path, str(e), traceback.format_exc())

def process_images_multiprocess(img_paths, num_processes=None, overwrite=False):
    """
    使用多进程处理图像转换
    :param img_paths: 图像路径列表
    :param num_processes: 进程数，None为自动设置
    :param overwrite: 是否覆盖已存在的文件
    """
    if num_processes is None:
        num_processes = min(cpu_count(), len(img_paths))
    
    print(f"使用 {num_processes} 个进程处理 {len(img_paths)} 张图片...")
    
    # 准备参数
    args = [(path, overwrite) for path in img_paths]
    
    failed_files = []
    
    with Pool(processes=num_processes) as pool:
        # 使用imap_unordered和tqdm显示进度
        results = list(tqdm(pool.imap_unordered(process_image_to_shp, args),
                      total=len(img_paths),
                      desc="处理进度"))
    
    # 收集失败的文件
    for result in results:
        if result is not None:
            failed_files.append(result)
    
    # 打印结果
    print(f"\n处理完成! 成功处理 {len(img_paths) - len(failed_files)} 张图片")
    if failed_files:
        print(f"失败的图片 ({len(failed_files)} 张):")
        for file, error, trace in failed_files:
            print(f"文件: {file}")
            print(f"错误: {error}")
            # 如需详细堆栈跟踪，取消下面注释
            # print(f"堆栈跟踪:\n{trace}")
            print("-" * 50)

def main():
    # 图像目录
    image_dir = r'D:\Ai\sv\半球_fisheye_01'
    
    # 支持的图像格式
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    # 收集所有图像路径
    img_paths = []
    for root, _, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(image_types):
                img_paths.append(os.path.join(root, file))
    
    if not img_paths:
        print("未找到任何图像文件!")
        return
    
    # 设置进程数 (None为自动设置)
    num_processes = None
    
    # 是否覆盖已存在的文件
    overwrite = False
    
    # 处理图像
    process_images_multiprocess(img_paths, num_processes, overwrite)

if __name__ == '__main__':
    main()