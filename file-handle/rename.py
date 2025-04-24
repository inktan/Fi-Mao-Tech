import os

# 定义文件夹路径
folder_path = r'E:\work\sv_goufu\MLP\year21\汇总数据-点'

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 构建完整的文件路径
    old_filepath = os.path.join(folder_path, filename)
    
    # 确保是文件而不是子文件夹
    if os.path.isfile(old_filepath):
        # 替换文件名中的"MLP"为"year"
        new_filename = filename.replace('MLP', 'year')
        
        # 只有当文件名确实改变时才重命名
        if new_filename != filename:
            new_filepath = os.path.join(folder_path, new_filename)
            
            # 执行重命名操作
            try:
                os.rename(old_filepath, new_filepath)
                print(f'已重命名: {filename} -> {new_filename}')
            except Exception as e:
                print(f'重命名失败: {filename}, 错误: {str(e)}')