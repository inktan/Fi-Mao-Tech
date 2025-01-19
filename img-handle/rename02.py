import pandas as pd
import os

image_folder =r'D:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02'

roots = []
img_names = []
img_paths = []

accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")

for root, dirs, files in os.walk(image_folder):
    for file in files:
        if file.endswith(accepted_formats) and file.startswith('pan00_'):
            roots.append(root)
            img_names.append(file)
            file_path = os.path.join(root, file)
            img_paths.append(file_path)

print(len(img_paths))

