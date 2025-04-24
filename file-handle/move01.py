import os
import shutil

def process_images(source_folder, target_folder):
    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # 获取所有jpg文件
    image_files = [f for f in os.listdir(source_folder) if f.lower().endswith('.jpg')]
    
    # 创建一个字典来存储文件名前四项和对应的文件信息
    file_dict = {}
    
    # 第一次遍历：收集所有文件信息
    for filename in image_files:
        parts = filename.split('_')
        if len(parts) < 5:
            continue  # 不符合命名规则的文件跳过
        
        # 获取前四项作为键
        key = '_'.join(parts[:4])
        
        # 尝试获取第五部分的数字
        try:
            num = int(parts[4].split('.')[0])  # 去掉.jpg后缀后转数字
        except ValueError:
            continue  # 如果第五部分不是数字则跳过
        
        # 存储文件信息
        if key not in file_dict:
            file_dict[key] = []
        file_dict[key].append({'filename': filename, 'num': num})
    
    # 第二次遍历：处理重复文件
    for key, files in file_dict.items():
        if len(files) > 1:  # 有重复文件
            # 找到数字最大的文件
            max_num_file = max(files, key=lambda x: x['num'])
            
            # 移动其他文件
            for file_info in files:
                if file_info != max_num_file:
                    src_path = os.path.join(source_folder, file_info['filename'])
                    dst_path = os.path.join(target_folder, file_info['filename'])
                    shutil.move(src_path, dst_path)
                    print(f"Moved: {file_info['filename']}")

# 使用示例
source_folder = r'E:\work\sv_quanzhou\sv_pan'
target_folder = r'E:\work\sv_quanzhou\sv_pan01'

process_images(source_folder, target_folder)
print("处理完成！")