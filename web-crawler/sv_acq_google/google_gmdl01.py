import pygmdl
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
    
    # img_file_format = '.jpg'
    img_file_format = '.png'

    number_of_tiles = 1
    # for zoom in [22,,,20,18,16]:
    for zoom in [19]:
        # 杭州天目里
        lon = 120.0946157506
        lat = 30.2688266736
        coords = [
        (lon,lat),
        ]

        for zoom in [20]:
            for size in [100]:
                output_path = f"E:\\temp\\sate_img\\{coords[0][0]}_{coords[0][1]}_{size}m_{zoom}_satellite_image.jpg"
                if os.path.exists(output_path):
                    continue
                try:
                    pygmdl.save_image(lat, lon, size, output_path, rotation, zoom, True)
                except Exception:  # pylint: disable=W0718
                    pass 
        # break
