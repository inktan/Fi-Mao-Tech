import os
from PIL import Image
from tqdm import tqdm

# Define the directory path
directory_path = r"E:\work\sv_LDW\zoom0"

img_paths = []
roots = []
img_names = []

for root, dirs, files in os.walk(directory_path):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for img_path in tqdm(img_paths):
    img = Image.open(img_path)
    
    # print(img.size)
    if img.size == (768, 768):
        top = (768 - 576) // 2
        bottom = top + 576
        
        cropped_img = img.crop((0, top, 768, bottom))
        
        img_path = img_path.replace('zoom0', 'sv_zoom0')
        folder_path = os.path.dirname(img_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        cropped_img.save(img_path)

