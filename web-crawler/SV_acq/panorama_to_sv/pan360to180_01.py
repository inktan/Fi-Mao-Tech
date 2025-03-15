
from PIL import Image
import os
from tqdm import tqdm

def create_intervals(base_number):
    interval_1 = (base_number - 90, base_number + 90)
    interval_2 = (interval_1[0] + 90, interval_1[1] + 90)

    if interval_2[1] > 360:
        return [(interval_2[0], 360), (0, interval_2[1] - 360)]
    else:
        return [interval_2]

def map_interval(interval, width):
    start = int(interval[0] / 360 * width)
    end = int(interval[1] / 360 * width)
    return start, end

def crop_and_concatenate(image_path, interval):
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"错误：找不到图像文件 {image_path}")
        return None

    width, height = img.size

    # 映射区间到图像宽度
    if len(interval) != 2:
        crop_start1, crop_end1 = map_interval(interval[0], width)
        # 裁剪图像
        cropped_img1 = img.crop((crop_start1, 0, crop_end1, height))
        # 拼接图像
        new_width = cropped_img1.width
        new_img = Image.new("RGB", (new_width, height))
        new_img.paste(cropped_img1, (0, 0))
        return new_img
    else:
        crop_start1, crop_end1 = map_interval(interval[0], width)
        crop_start2, crop_end2 = map_interval(interval[1], width)
        # 裁剪图像
        cropped_img1 = img.crop((crop_start1, 0, crop_end1, height))
        cropped_img2 = img.crop((crop_start2, 0, crop_end2, height))
        # 拼接图像
        new_width = cropped_img1.width + cropped_img2.width
        new_img = Image.new("RGB", (new_width, height))
        new_img.paste(cropped_img1, (0, 0))
        new_img.paste(cropped_img2, (cropped_img1.width, 0))
        return new_img

# input_image_path = "e:\work\zhanshubaigeiyiwan\\180度照片朝向\sv_正东朝向01\sv_pan\\0_113.0386219_28.19609746_202209.jpg"
# output_image_path = r"E:\work\zhanshubaigeiyiwan\180度照片朝向\cropped_panorama.jpg"
# center_angle = 270 

# center_angles = create_intervals(center_angle)
# new_img = crop_and_concatenate(input_image_path, center_angles)

# new_img.save(output_image_path)

# 定义图片文件类型  
image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
# 遍历输入文件夹中的所有图片文件，并进行处理
img_paths = []
roots = []
img_names = []

for root, dirs, files in os.walk(r'e:\work\zhanshubaigeiyiwan\180度照片朝向\sv_正西朝向01\sv_pan'):
    for file in files:
        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)
            img_names.append(file)
            roots.append(root)

for input_image_path in tqdm(img_paths):
    img_degree_save = input_image_path.replace('sv_pan','sv_pan_180')
    if os.path.exists(img_degree_save):
        continue

    center_angle = 270 
    center_angles = create_intervals(center_angle)
    new_img = crop_and_concatenate(input_image_path, center_angles)

    folder_path = os.path.dirname(img_degree_save)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    new_img.save(img_degree_save)
