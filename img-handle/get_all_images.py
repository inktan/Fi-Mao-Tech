import os
import json
import string
import random
import os
import shutil
from tqdm import tqdm
import json
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

def get_all_image_files(base_path):
    # 定义支持的图片文件扩展名
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
    # 存储找到的图片文件路径
    image_files = set()
    unique_directories = set()

    # 遍历base_path下的所有文件和文件夹
    for root, dirs, files in os.walk(base_path):
        for file in files:
            # 检查文件扩展名是否为图片格式
            if any(file.lower().endswith(ext) for ext in image_extensions):
                # 如果是图片文件，添加到列表中
                image_files.add(os.path.join(root, file))
                unique_directories.add(root)

    return image_files,unique_directories

unique_numbers = set()
def generate_unique_random_number(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def move_file_with_folder_creation(foloder_path):
    image_files,unique_directories = get_all_image_files(foloder_path)

    # 使用tqdm和enumerate循环
    for index, item in tqdm(enumerate(unique_directories), total=len(unique_directories)):
        try:
            with open(item+'\project_info.json', 'r') as file:
                data = json.load(file)
                path_name_guid = data['project_info']['path_name_guid']

            folder_prefix = r"D:\Ai-clip-seacher\Ai_Basic_Architecture_Library_01\goa_"
            goa_index = (index+1)//5000+1

            dest_folder_path = folder_prefix + str(goa_index)+'\\'+path_name_guid
            # 检查目标文件夹是否存在，如果不存在则创建
            if not os.path.exists(dest_folder_path):
                os.makedirs(dest_folder_path)

            # 遍历源文件夹中的所有文件和子文件夹
            for sub_item in os.listdir(item):
                source_item = os.path.join(item, sub_item)
                destination_item = os.path.join(dest_folder_path, sub_item)
                
                # 移动文件或文件夹
                # if os.path.isdir(source_item):
                    # 如果是文件夹，则递归移动文件夹内容
                shutil.move(source_item, destination_item)
                # else:
                    # 如果是文件，则直接移动
                    # shutil.move(source_item, dest_folder_path)
        except Exception as e:
                print(e)

def add_json(foloder_path):
    image_files,unique_directories = get_all_image_files(foloder_path)
    for directory_path in unique_directories:

        parts = directory_path.split('\\')

        index = parts.index('Ai_Basic_Architecture_Library')
        extracted_parts = parts[index+1:]

        path_dict = {}
    
        str_guid = generate_unique_random_number(10)
        while (1):
            if str_guid not in unique_numbers:
                unique_numbers.add(str_guid)
                break
            else:
                str_guid = generate_unique_random_number(10)
        path_dict[f"path_name_guid"] = str_guid

        for i, value in enumerate(extracted_parts):
            path_dict[f"path_name_{str(i+1).zfill(2)}"]= value
                
        # Define the JSON content
        json_content = {
            "project_info": path_dict,
        }

        json_file_path = os.path.join(r"\\?\\" + directory_path, 'project_info.json')

        # Create and write to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(json_content, json_file)

    print(len(image_files)) 
    print(len(unique_directories))


def resize(image_directory):
    TARGET_PIXELS = 1024 * 1024  # 1K像素的平方
    image_files,unique_directories =get_all_image_files(image_directory)
    for file_path in tqdm( image_files):
        try:
            with Image.open(file_path) as img:
                img_size = img.size
                img_pixels = img_size[0] * img_size[1]
                # if img_pixels > TARGET_PIXELS:
                #     scale = TARGET_PIXELS ** 0.5 / max(img_size)
                #     new_size = (int(img_size[0] * scale), int(img_size[1] * scale))
                #     img_resized = img.resize(new_size)
                #     img_resized.save(file_path)
        except Exception as e:
            print(e)

def resize_width200px(image_directory):
    image_files,unique_directories =get_all_image_files(image_directory)
    for file_path in image_files:
        try:
            with Image.open(file_path) as img:
                # 检查图片宽度
                if img.width != 200:
                    new_height = int((200 / img.width) * img.height)
                    img = img.resize((200, new_height), Image.ANTIALIAS)
                    img.save(file_path.replace('AiArchLib1k','AiArchLib200px'))
            
        except Exception as e:
            print(e)
            
# def main02():
    # 复制整个文件夹及其内容到新位置
    # shutil.copytree(source_directory, destination_directory)

if __name__ == "__main__":
    image_directory = r'D:\Ai-clip-seacher\AiArchLib' 
    # move_file_with_folder_creation(destination_directory)
    resize(image_directory)
    



