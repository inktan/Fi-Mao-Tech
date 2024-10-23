import os  
from tqdm import tqdm
from PIL import Image

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

# 指定你想要遍历的文件夹路径  
folder_path = r'e:\work\sv_levon\sv_degree_new'  

# 自定义排序键：根据后缀中的数字排序  
def sort_key(file_path):  
    # 提取文件名中的数字部分（即后缀中的角度值）  
    angle = int(file_path.split('_')[-1].split('.')[0])  
    # 定义一个顺序列表，用于映射角度值到排序顺序  
    order = {0: 0, 90: 1, 180: 2, 270: 3}  
    # 返回映射后的顺序值  
    return order[angle]  
  
for item in tqdm(os.listdir(folder_path)):
    source_folder = os.path.join(folder_path, item)
    if os.path.isdir(source_folder):

        img_paths = []
        img_names = []

        accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

        for root, dirs, files in os.walk(source_folder):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)

        img_paths = sorted(img_paths, key=sort_key)

        print(len(img_paths))
        if len(img_paths) == 4:

            directory = r'e:\\work\\sv_levon\\sv_degree_hor'
            if not os.path.exists(directory):
                os.makedirs(directory)

            output_image_path = os.path.join(directory, img_names[0].replace('_0.jpg', '_hor.jpg'))

            combine_images_optimized(img_paths, output_image_path)


