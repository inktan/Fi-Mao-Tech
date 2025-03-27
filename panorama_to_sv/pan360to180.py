
import numpy as np
from PIL import Image
import os
from tqdm import tqdm

def panorama_to_sphere(panorama_image):
    width, height = panorama_image.size
    sphere_image = Image.new('RGB', (width, height))
    sphere_pixels = np.zeros((height, width, 3), dtype=np.uint8)

    x = np.arange(width)
    y = np.arange(height)
    x, y = np.meshgrid(x, y)

    theta = 2 * np.pi * x / width
    phi = np.pi * y / height
    sphere_radius = height / np.pi

    sphere_x = (sphere_radius * np.sin(phi) * np.cos(theta)).astype(int)
    sphere_y = (sphere_radius * np.sin(phi) * np.sin(theta)).astype(int)
    sphere_z = (sphere_radius * np.cos(phi)).astype(int)

    panorama_pixels = np.array(panorama_image)

    panorama_x = (width * (theta / (2 * np.pi))).astype(int) % width
    panorama_y = (height * (phi / np.pi)).astype(int) % height

    sphere_pixels = panorama_pixels[panorama_y, panorama_x]
    sphere_image = Image.fromarray(sphere_pixels)

    return sphere_image

def rotate_sphere(sphere_image, angle):
    width, height = sphere_image.size
    rotated_image = Image.new('RGB', (width, height))
    sphere_pixels = np.array(sphere_image)

    x = np.arange(width)
    theta = 2 * np.pi * x / width
    angle_rad = np.radians(angle)
    rotated_theta = theta + angle_rad

    rotated_x = (width * (rotated_theta / (2 * np.pi))).astype(int) % width
    rotated_pixels = sphere_pixels[:, rotated_x]
    rotated_image = Image.fromarray(rotated_pixels)

    return rotated_image

def extract_180_sphere(sphere_image):
    width, height = sphere_image.size
    extracted_width = int(width / 2)
    sphere_pixels = np.array(sphere_image)

    extracted_pixels = sphere_pixels[:, :extracted_width]
    extracted_image = Image.fromarray(extracted_pixels)

    return extracted_image

def sphere_to_panorama(sphere_image_180):
    width, height = sphere_image_180.size
    panorama_width = 2048
    panorama_height = 2048
    panorama_image = Image.new('RGB', (panorama_width, panorama_height))
    sphere_pixels = np.array(sphere_image_180)

    x = np.arange(panorama_width)
    y = np.arange(panorama_height)
    x, y = np.meshgrid(x, y)

    theta = np.pi * x / panorama_width
    phi = np.pi * y / panorama_height

    sphere_x = (width * (theta / np.pi)).astype(int) % width
    sphere_y = (height * (phi / np.pi)).astype(int) % height

    panorama_pixels = sphere_pixels[sphere_y, sphere_x]
    panorama_image = Image.fromarray(panorama_pixels)

    return panorama_image
def main():
    # 读取全景图
    # input_image_path = "e:\work\zhanshubaigeiyiwan\\180度照片朝向\sv_正东朝向01\sv_pan\\0_113.0386219_28.19609746_202209.jpg"
    # image = pil_to_cv2(input_image_path)
    
    # 定义图片文件类型  
    image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        
    # 遍历输入文件夹中的所有图片文件，并进行处理
    img_paths = []
    roots = []
    img_names = []

    for root, dirs, files in os.walk(r'e:\work\zhanshubaigeiyiwan\180度照片朝向\sv_正南朝向01\sv_pan'):
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

        # 加载全景图
        panorama_image = Image.open(input_image_path)
        # 全景图转球形图
        sphere_image = panorama_to_sphere(panorama_image)
        # 调整镜头视角（例如，旋转120°）
        rotated_sphere_image = rotate_sphere(sphere_image, 180)
        # 提取180°球形图
        sphere_image_180 = extract_180_sphere(rotated_sphere_image)
        # 180°球形图转全景图
        panorama_image_180 = sphere_to_panorama(sphere_image_180)
        # 保存结果

        folder_path = os.path.dirname(img_degree_save)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        panorama_image_180.save(img_degree_save)

if __name__ == "__main__":
    main()



