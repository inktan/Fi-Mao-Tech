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
folder_path = r'e:\work\sv_wenhan_levon\20251211\sv_pan01'
  
img_paths = []
img_names = []
accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(accepted_formats):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)

print(len(img_paths))

for image in tqdm(img_paths,total=len(img_paths)):
    
    angle_suffixes = ['_0', '_60', '_120', '_180', '_240', '_300']
    angle_suffixes = ['_0', '_90', '_180', '_270']
    image_paths = [image.replace('.jpg', suffix + '.jpg').replace('sv_pan01', '街景') for suffix in angle_suffixes]
    
    combine_images_optimized(image_paths, image.replace('sv_pan01', 'sv_街景_hor').replace('.jpg', '_hor.jpg'))

