import pygmdl
from coord_convert import transform

# 从google map量去的坐标为gcj-2，需要转为wgs84
coords = [
(120.099429798568,30.266375920049807),
]
# 将 GCJ-02 坐标转换为 WGS84 坐标
wgs_coords = [transform.gcj2wgs(lng, lat) for lng, lat in coords]

size = 300
rotation = 0
from_center = True

for zoom in [22,20,18,16]:

    lon=wgs_coords[0][0]
    lat=wgs_coords[0][1]
    output_path = f"C:\\Users\\wang.tan.GOA\\Pictures\\Screenshots\\{coords[0][0]}_{coords[0][1]}_{size}m_{zoom}_satellite_image.png"

    pygmdl.save_image(lat, lon, size, output_path, rotation, zoom, from_center)