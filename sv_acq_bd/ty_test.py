import cv2
import numpy as np
from PIL import Image  
import os
import cv2
from tqdm import tqdm
import numpy as np
import time
from tqdm import tqdm
Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

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
    def __init__(self, img):

        # 使用PIL读取图像  
        #pil_image = Image.open(img_name)  
        pil_image = img
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
    
def remove_black_borders(image):
    """去除图像中的黑边"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image
def load_image(path, target_size):
    try:
        e_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if e_img is None:
            raise ValueError(f"Error loading image at path: {path}")
        
        # total_pixels = e_img.shape[0] * e_img.shape[1]
        # black_pixels = np.sum(np.all(e_img[:, :, :3] == [0, 0, 0], axis=-1))
        # black_pixel_ratio = black_pixels / total_pixels
        # if black_pixel_ratio > 0.10:
        e_img = remove_black_borders(e_img)
        e_img = cv2.resize(e_img, target_size, interpolation=cv2.INTER_LINEAR)

        if e_img.shape[-1] == 4:  # RGBA
            e_img = cv2.cvtColor(e_img, cv2.COLOR_BGRA2RGBA)
        else:
            e_img = cv2.cvtColor(e_img, cv2.COLOR_BGR2RGB)

        pillow_img = Image.fromarray(e_img)
        return pillow_img
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
import csv
def panorama_to_street_view():
  with open(r'e:\work\sv_YJ_20240924\points\los_angeles_panoid_only_latest_year_unique_pano_id.csv', 'r') as f:
    reader = csv.reader(f)
    mylist = list(reader)
    count = 0
    # print(mylist)
    for row in tqdm(mylist):
      count += 1
      if count == 1 or len(row)<3:
          continue

      if count <= 154500:
         continue
      #if count >15200000000:
      #    continue

      building_id_ori = row[2]
      categories_ori = row[3]
      heading_ori = row[4]
      heading = row[11]

      adjusted_heading = (float(heading) - float(heading_ori) + 180) % 360 - 180
      pitch=0
      fov = 110




      pano_id = row[8]
      try :
        img_save_path = r'e:\work\sv_YJ_20240924\points\test' + f"/{pano_id}.jpg"
        if os.path.isfile(img_save_path):
          print(img_save_path + '存在')
          e_img = load_image(img_save_path, (15360, 7680))  # 添加缩放尺寸
          equ = Equirectangular(e_img)    # Load equirectangular image
          e_img = equ.GetPerspective(fov, adjusted_heading, pitch,3000,3000) 
          img_save_path = r'e:\work\sv_YJ_20240924\points\test_clip' + f"/{building_id_ori}_{categories_ori}.png"

          cv2.imwrite(img_save_path, e_img)
        #   break
        else:
          continue
      except Exception as e :
        print(f'error:{e}')
        continue
      
panorama_to_street_view()