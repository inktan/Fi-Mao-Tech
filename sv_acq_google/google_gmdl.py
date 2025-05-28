import pygmdl
from coord_convert import transform
import os

# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(120.09944541288698,30.266322523956244),
]

# 将 GCJ-02 坐标转换为 WGS84 坐标
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]

size = 100
rotation = 0
from_center = True

# for zoom in [22,,,20,18,16]:
for zoom in [22,20,18,16]:

    lon=wgs_coords[0][0]
    lat=wgs_coords[0][1]
    output_path = f"E:\\work\\spatio_evo_urbanvisenv_svi_leo371\\街道分类\\街景\\{coords[0][0]}_{coords[0][1]}_{size}m_{zoom}_satellite_image.jpg"
    # os.makedirs(output_path, exist_ok=True)

    pygmdl.save_image(lat, lon, size, output_path, rotation, zoom, from_center)


