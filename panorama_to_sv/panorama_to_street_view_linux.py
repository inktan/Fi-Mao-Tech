# -*- coding: utf-8 -*-

import os
import cv2
import os  
from tqdm import tqdm
from PIL import Image  
import numpy as np  
import cv2
import numpy as np

from PIL import Image  

def xyz2lonlat(xyz):
    atan2 = np.arctan2
    asin = np.arcsin

    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    xyz_norm = xyz / norm
    x = xyz_norm[..., 0:1]
    y = xyz_norm[..., 1:2]
    z = xyz_norm[..., 2:]

    lon = atan2(x, z)
    lat = asin(y)
    lst = [lon, lat]

    out = np.concatenate(lst, axis=-1)
    return out

def lonlat2XY(lonlat, shape):
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    lst = [X, Y]
    out = np.concatenate(lst, axis=-1)

    return out 

class Equirectangular:
    def __init__(self, img_name):

        # 使用PIL读取图像  
        pil_image = Image.open(img_name)  
        # 将PIL图像转换为OpenCV格式  
        self._img = np.array(pil_image)[:, :, ::-1].copy()  # 注意：PIL使用RGB顺序，而OpenCV使用BGR顺序

        # self._img = cv2.imread(img_name, cv2.IMREAD_COLOR)
        [self._height, self._width, _] = self._img.shape
        #cp = self._img.copy()  
        #w = self._width
        #self._img[:, :w/8, :] = cp[:, 7*w/8:, :]
        #self._img[:, w/8:, :] = cp[:, :7*w/8, :]    

    def GetPerspective(self, FOV, THETA, PHI, height, width):
        #
        # THETA is left/right angle, PHI is up/down angle, both in degree
        #

        f = 0.5 * width * 1 / np.tan(0.5 * FOV / 180.0 * np.pi)
        cx = (width - 1) / 2.0
        cy = (height - 1) / 2.0
        K = np.array([
                [f, 0, cx],
                [0, f, cy],
                [0, 0,  1],
            ], np.float32)
        K_inv = np.linalg.inv(K)
        
        x = np.arange(width)
        y = np.arange(height)
        x, y = np.meshgrid(x, y)
        z = np.ones_like(x)
        xyz = np.concatenate([x[..., None], y[..., None], z[..., None]], axis=-1)
        xyz = xyz @ K_inv.T

        y_axis = np.array([0.0, 1.0, 0.0], np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], np.float32)
        R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
        R = R2 @ R1
        xyz = xyz @ R.T
        lonlat = xyz2lonlat(xyz) 
        XY = lonlat2XY(lonlat, shape=self._img.shape).astype(np.float32)
        persp = cv2.remap(self._img, XY[..., 0], XY[..., 1], cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)

        return persp
    
def panorama_to_street_view(input_dir,fov,degree_count,phi,height,width):
      
    # 定义图片文件类型  
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')  
        
    # 遍历输入文件夹中的所有图片文件，并进行处理
    img_paths = []
    roots = []
    img_names = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)
                roots.append(root)

    for i,image_path in enumerate(tqdm(img_paths)): 
        # 判断文件是否为图片类型  
        if image_path.lower().endswith(image_types):
            # if i<14390:
            #     continue
            # if i==20:
            #     break
            try:
                equ = Equirectangular(image_path)    # Load equirectangular image

                degree_avg = 360 / degree_count
                degrees = [i*degree_avg for i in range(degree_count)]
                # degrees = [90]
                
                image_type = image_path.split('.')[-1]
                for i in degrees:
                    img_degree_save = image_path.replace('sv_pan',f'sv_degree_{width}_{height}').replace('.'+image_type,'_'+str(int(i))+'.'+image_type)
                    if os.path.exists(img_degree_save):
                        continue

                    img = equ.GetPerspective(fov, i, phi,height,width) # Specify parameters(FOV, theta, phi, height, width)
                    persp_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(persp_rgb)

                    folder_path = os.path.dirname(img_degree_save)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    pil_image.save(img_degree_save)  # 可以保存为.jpg、.png等格式
                    # cv2.imwrite(img_degree_save,img)
           
            except Exception as e:
                print(e)

# ------------Main Function -------------------
if __name__ == "__main__":
    input = r'F:\sv_shanghai\sv_pan'

    # fov是镜头的远近关系 水平方向范围，范围[10,360]，fov=360即可显示整幅全是图
    # pitch是仰头，低头关系 垂直视角，范围[0,90]。
    # heading是东南西北旋转关系 水平视角，范围[0.360]
    fov = 90
    phi = 0

    # 角度个数
    degree_count = 4

    # 角度街景宽度
    width = 960
    height = 720
    
    panorama_to_street_view(input ,fov,degree_count,phi,height,width)

















