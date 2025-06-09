import pygmdl
from coord_convert import transform
import os
import os
from coord_convert import transform
from tqdm import tqdm

if __name__ == '__main__':

    # zoom = 15 # 256*256的瓦片尺寸为1760*1760m     每个像素点为6.88m
    # zoom = 16 # 256*256的瓦片尺寸为880*880m       每个像素点为3.44m
    zoom = 17 # 256*256的瓦片尺寸为440*440m       每个像素点为1.72m
    # zoom = 18 # 256*256的瓦片尺寸为220*220m       每个像素点为0.86m
    zoom = 19 # 256*256的瓦片尺寸为110*110m         每个像素点为0.43m
    # zoom = 20 # 无卫星图

    rotation = 0
    # size = 200
    size = 500
    
    number_of_tiles = 1
    # img_file_format = '.jpg'
    img_file_format = '.png'

    tasks = []
    target_dir = r"E:\work\spatio_evo_urbanvisenv_svi_leo371\街景建筑分类"
    for root, dirs, files in os.walk(target_dir):
        # 检查当前目录是否有文件，且没有子文件夹
        if files and not dirs:
            folder_name = os.path.basename(root)
            tasks.append([folder_name,root])

    for folder_name, root in tqdm(tasks):
        # 杭州天目里
        lon = folder_name.split('_')[-2]
        lat = folder_name.split('_')[-1]
        # output_path = root + f"\\{lon}_{lat}_{size}m_{zoom}_bs.jpg"

        # 转为bd09
        # lon,lat = transform.wgs2bd(float(lon),float(lat))
        # continue

        for zoom in [20]:
            for size in [100]:
                output_path = root + f"\\{size}m_{zoom}_gs.jpg"
                if os.path.exists(output_path):
                    continue
                try:
                    pygmdl.save_image(lat, lon, size, output_path, rotation, zoom, True)
                except Exception:  # pylint: disable=W0718
                    pass 
        # break
