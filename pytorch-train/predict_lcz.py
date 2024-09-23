from tqdm import tqdm
import torch
from torchvision import transforms,datasets,models
import os
import pandas as pd
from torch.utils.data import Dataset, DataLoader 
from PIL import Image
import rasterio  
import numpy as np  
from scipy.ndimage import zoom  
from osgeo import gdal  
import cv2
import matplotlib.pyplot as plt
import random 
import csv

torch.cuda.empty_cache()

# 随机生成RGB颜色值  
def generate_random_color():  
    r = random.randint(0, 255)  
    g = random.randint(0, 255)  
    b = random.randint(0, 255)  
    return (r, g, b)
 # 读取单通道tif图并存储为numpy数组  
def read_tif_as_numpy(file_path):  
    with rasterio.open(file_path) as src:  
        return src.read(1)  # 读取第一个通道（对于单通道图像来说就是整个图像）
       
def predict(model,device,predictn_folder,out_folder):
    row_ =['x', 'y', 'lcz_label','lcz_color']
    with open(r'd:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m\lcz.csv','w' ,newline='') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(row_)
        except:
            print()

    model.to(device)

    with torch.no_grad():  
        model.eval()

        # 打开8个单通道tif图并存储为numpy数组  
        tif_files =  ['B1','B2','B3','B4','B5','B6','B7','B9','B10','B11']
        tif_files = [predictn_folder+'\spatial_10m'+i+'.tif' for i in tif_files]
        images = [read_tif_as_numpy(file) for file in tif_files]  

        # 定义裁切框大小和步长  
        crop_size = (32, 32)

        # 创建空白画布  
        width_lcz = images[0].shape[0]//crop_size[0]
        height_lcz = images[0].shape[1]//crop_size[1]
        # 创建空白画布  
        canvas = Image.new('RGB', (width_lcz, height_lcz))  
        # 从左上角开始，从左往右，从上往下进行滚动裁切  
        for i in range(0, width_lcz):  
            for j in tqdm(range(0, height_lcz)):  
                # random_color = generate_random_color() 
                # canvas.putpixel((i, j), random_color)  

                # 定义裁切框的起始和结束坐标  
                row_start, row_end = i*crop_size[0], (i + 1) * crop_size[0]  
                col_start, col_end = j*crop_size[1], (j + 1) * crop_size[1]  
                
                # 对每个通道的图像进行裁切  
                cropped_images = [img[row_start:row_end, col_start:col_end] for img in images]  
                
                # 将8个裁切后的数据合并为一个8通道的数据块
                cropped_block = np.dstack(cropped_images)  
            
                cropped_block =  cropped_block.astype(np.float32)  
                cropped_block_tensor = torch.from_numpy(cropped_block) 
                cropped_block_tensor = cropped_block_tensor.permute(2, 0, 1)

                cropped_block_tensor = cropped_block_tensor.unsqueeze_(0)
                cropped_block_tensor = cropped_block_tensor.to(device)

                outputs = model(cropped_block_tensor)
                probs, out_label = outputs.max(axis=1)
                out_label = out_label.detach().cpu().numpy()

                # 17组颜色  
                label = [(165, 0, 33),
                        (204, 0, 0),
                        (255, 0, 0),
                        (153, 51, 0),
                        (204, 102, 0),
                        (255, 153, 0),
                        (255, 255, 0),
                        (192, 192, 192),
                        (255, 204, 153),
                        (77, 77, 77),
                        (0, 102, 0),
                        (21, 255, 21),
                        (102, 153, 0),
                        (204, 255, 102),
                        (0, 0, 102),
                        (255, 255, 204),
                        (51, 102, 255)]
                
                canvas.putpixel((i, j), label[out_label[0]])  
                row_ =[i, j,out_label[0], label[out_label[0]]]
                
                with open(r'd:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m\lcz.csv','a' ,newline='') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerow(row_)
                    except:
                        print()

        canvas.save(out_folder +'/lcz.png')

        print(f'预测结束，已结果文件生成文件，地址位{out_folder}')

from osgeo import gdal  
def process_spatial_resolution_tif():
    '''上采样tif文件，从30m到10m'''
    # 打开tif文件  
    for i in ['B1','B1''B1','B2','B3','B4','B5','B6','B7','B8','B9','B10','B11']:
        tif_file = r"D:\ProgramData\GitHub\LCZ_MSMLA\data\LC08_L1TP_120033_20230823_20230826_02_T1\LC08_L1TP_120033_20230823_20230826_02_T1_"+ i +".TIF"  
        if i=='B8': # B8为15m，这里忽略
            continue
        else: 
            # 打开 TIFF 文件
            with Image.open(tif_file) as img:
                # 获取原始图像的尺寸
                width, height = img.size

                # 计算新的尺寸。因为分辨率从 30m 提高到 10m，
                # 所以新的尺寸应该是原始尺寸的三倍
                new_width = width * 3
                new_height = height * 3

                # 使用 NEAREST, BILINEAR, BICUBIC 或 LANCZOS 滤镜之一进行上采样
                # 这里我使用 BICUBIC 作为示例
                resized_img = img.resize((new_width, new_height), Image.BICUBIC)

                # 保存上采样后的图像
                resized_img.save(r'D:\ProgramData\GitHub\LCZ_MSMLA\data\saptial_10m'+ i +'.tif')

def process_spatial_resolution_tif():
    '''
    空间分辨率为30m，上采样到10m
    '''
    for i in tqdm(['B1','B2','B3','B4','B5','B6','B7','B8','B9','B10','B11']):
        tif_file = r"D:\ProgramData\GitHub\LCZ_MSMLA\data\LC08_L1TP_120033_20230823_20230826_02_T1\LC08_L1TP_120033_20230823_20230826_02_T1_"+ i +".TIF"  
        if i=='B8': # B8为15m，这里忽略
            continue
        else: 
            # 打开TIF文件  
            with rasterio.open(tif_file) as src:  
                band = src.read(1)  # 读取第一波段数据  
                transform = src.transform  # 获取地理变换信息  
                crs = src.crs  # 获取坐标参考系  
                nodata = src.nodata  # 获取无数据值  
            
            # 上采样  
            scale_factor = 3  # 目标分辨率与原始分辨率的比例  
            upsampled_band = zoom(band, scale_factor, order=3, mode='nearest')  # 使用最近邻插值进行上采样  
            
            # 创建输出文件  
            output_meta = src.meta.copy()  
            output_meta.update({  
                'driver': 'GTiff',  
                'height': upsampled_band.shape[0],  
                'width': upsampled_band.shape[1],  
                'transform': rasterio.Affine(transform.a / scale_factor, transform.b, transform.c,  
                                            transform.d, transform.e / scale_factor, transform.f),  
                'crs': crs,  
                'nodata': nodata  
            })  
            
            # 保存输出文件  
            with rasterio.open(r'D:\ProgramData\GitHub\LCZ_MSMLA\data\saptial_10m\\'+ i +'.tif', 'w', **output_meta) as dst:  
                dst.write(upsampled_band, 1)
    
def read_tif(tif_file):
    # 打开tif文件  
    dataset = gdal.Open(tif_file, gdal.GA_ReadOnly)  
    # 获取图像的宽度和高度  
    width = dataset.RasterXSize  
    height = dataset.RasterYSize  
    # 获取图像的波段数  
    bands = dataset.RasterCount  
    # 读取第一个波段的数据  
    band1 = dataset.GetRasterBand(1)
    data = band1.ReadAsArray()
    # 打印数据的一些基本信息  
    print("Width: ", width)  
    print("Height: ", height)  
    print("Bands: ", bands)  
    print("Data type: ", data.dtype)  
    print("Data shape: ", data.shape)  
    print("Data min/max: ", data.min(), "/", data.max())
  
def crop_tif(output_folder, crop_size):  
    # 打开输入TIF文件
    for i in ['B1','B2','B3','B4','B5','B6','B7','B9']:

        tif_file = r"d:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m\spatial_10m\saptial_10m"+ i +".tif"
        directory_path = os.path.join(output_folder, i)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        with rasterio.open(tif_file) as src:  
            width = src.width  
            height = src.height
            i_ = 0  
            for i in tqdm(range(0, height, crop_size)): 
                j_ = 0 
                for j in range(0, width, crop_size):  
                    # 定义裁剪框  
                    window = rasterio.windows.Window(j, i, crop_size, crop_size)
                    
                    # 裁剪子区域  
                    sub_data = src.read(window=window)
                    
                    # 创建输出文件名  
                    output_file = os.path.join(directory_path, f'tile_{j_}_{i_}.tif')  
                    
                    # 保存裁剪后的子区域为新的TIF文件  
                    with rasterio.open(output_file, 'w', driver='GTiff', height=crop_size, width=crop_size, count=sub_data.shape[0], dtype=sub_data.dtype, crs=src.crs, transform=src.window_transform(window)) as dst:  
                        dst.write(sub_data)  
                    j_ += 1
                i_ += 1
                j_ = 0
  
if __name__ == "__main__":
    categories = ['lcz']
    # batch_size = 2

    predictn_folder = r'D:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m\spatial_10m'  # split into training(80%) and validation(20%)
    out_folder = r'D:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m'  # split into training(80%) and validation(20%)
    # predict_csv= f"D:/ProgramData/GitHub/LCZ_MSMLA/data/saptial_10m/{categories[0]}.csv"

    model_path= f"D:/ProgramData/GitHub/LCZ_MSMLA/data/{categories[0]}.pth"
    model = torch.load(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # predict_loader = load_dataset(predictn_folder, batch_size)
    predict(model,device,predictn_folder,out_folder)

    # process_spatial_resolution_tif()
    # i='B1'
    # i='B6'
    # tif_file = r"D:\ProgramData\GitHub\LCZ_MSMLA\data\saptial_10m\saptial_10m"+ i +".TIF"  
    # read_tif(tif_file)
    # pic = cv2.imread(tif_file)
    # print(type(pic))
    # print(pic.shape)
    # print(pic.size)
    # print(pic[5300, 5500])
    # print(pic[4500, 3500])
    # print(pic[5100, 6600])
    # print(pic[1200, 5000])

    # plt.imshow(pic)
    # print(pic[1200, 5200])
        
    # 设置输入和输出路径以及裁剪大小  
    # output_folder = r'd:\ProgramData\GitHub\LCZ_MSMLA\data\spatial_10m\spatial_10m_patch'  # 输出文件夹路径  
    # crop_size = 32  # 裁剪框大小  
    
    # 执行裁剪操作  
    # crop_tif(output_folder, crop_size)


