import csv
import os
import csv
import os
import shutil

def create_folders_and_copy_image(csv_file_path, image_path):
    # 检查 JPG 文件是否存在
    if not os.path.exists(image_path):
        print(f"指定的 JPG 文件 {image_path} 不存在。")
        return

    # 读取 CSV 文件
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 获取 name 列的值
            folder_name = row.get('name')
            if folder_name:
                # 去除文件夹名中的非法字符
                folder_name = ''.join(c for c in folder_name if c.isalnum() or c in (' ', '_', '-'))
                folder_path = os.path.join(os.getcwd(), folder_name)

                try:
                    # 创建文件夹
                    os.makedirs(folder_path, exist_ok=True)
                    print(f"成功创建文件夹: {folder_path}")

                    # 复制 JPG 文件到新创建的文件夹
                    shutil.copy2(image_path, folder_path)
                    print(f"成功将 {image_path} 复制到 {folder_path}")
                except Exception as e:
                    print(f"处理文件夹 {folder_name} 时出现错误: {e}")

def find_images(csv_file_path, image_folder_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if 'longitude' in row and 'latitude' in row:
                longitude = row['longitude']
                latitude = row['latitude']
                folder_name = row.get('name')
                combined_string = f"{longitude}_{latitude}"

                for filename in os.listdir(image_folder_path):
                    if combined_string in filename:
                        print(combined_string, filename)
                        image_path = os.path.join(image_folder_path, filename)

                        folder_path = os.path.join(r'E:\work\九条路', folder_name)
                        os.makedirs(folder_path, exist_ok=True)
                        shutil.copy2(image_path, folder_path)


# 示例使用
csv_file_path = r'e:\work\九条路\point_shp\points.csv'  # 替换为实际的CSV文件路径
image_folder_path = r'E:\work\九条路\sv_pan'  # 替换为实际的图片文件夹路径

# 调用函数查找匹配的图片
matched_images = find_images(csv_file_path, image_folder_path)