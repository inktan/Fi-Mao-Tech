import os  
from tqdm import tqdm
from PIL import Image
import os  
import shutil  

def combine_images_optimized(image_path_list, output_image_path):
    images = [Image.open(path) for path in image_path_list]
    width, height = images[0].size
    new_im = Image.new('RGB', (width * len(images), height), 'white')
    for idx, im in enumerate(images):
        new_im.paste(im, (idx * width, 0))
        
    directory = os.path.dirname(output_image_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    new_im.save(output_image_path)

# 自定义排序键：根据后缀中的数字排序
def sort_key(file_path):  
    # 提取文件名中的数字部分（即后缀中的角度值）  
    angle = int(file_path.split('_')[-1].split('.')[0])
    # 定义一个顺序列表，用于映射角度值到排序顺序  
    order = {0: 0, 90: 1, 180: 2, 270: 3}
    # 返回映射后的顺序值  
    return order[angle]

source_folder_new = r'E:\work\sv_levon\sv_points_1028\sv_pan_2017_sv_degree_960_720'
img_paths = []
img_names = []

accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(source_folder_new):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

count = 0
for i in tqdm(range(1, 10000)):
    file_paths = [source_folder_new+'\\'+name for name in img_names if name.startswith(f"{i}_")]
    if len(file_paths) == 4:
        sorted_file_paths = sorted(file_paths, key=sort_key)  
        output_image_path = sorted_file_paths[0].replace('_0.jpg','_hor.jpg').replace('sv_pan_2017_sv_degree_960_720','sv_2017_hor')
        combine_images_optimized(sorted_file_paths, output_image_path)

source_folder_new = r'E:\work\sv_levon\folder-01\sv_degree_hor_new'
source_folder_2017 = r'E:\work\sv_levon\folder-01\sv_degree_hor_2017'
img_paths_new = []
img_names_new = []
img_paths_2017 = []
img_names_2017 = []

accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(source_folder_new):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths_new.append(file_path)
            img_names_new.append(file)

for root, dirs, files in os.walk(source_folder_2017):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths_2017.append(file_path)
            img_names_2017.append(file)

count = 0
for i in range(1, 10000):
    img_name_new = [name for name in img_names_new if name.startswith(f"{i}_")]
    img_name_2017 = [name for name in img_names_2017 if name.startswith(f"{i}_")]

    # if len(img_name_2017) == 2:
    #     print(img_name_2017)

    if len(img_name_new) == 0 and len(img_name_2017) == 1:
        # print(img_name_new)
        print(img_name_2017)
        # count += 1
        # os.remove(r'E:\work\sv_levon\folder-01\sv_degree_hor_2017/'+img_name_2017[0])

# print(count)
