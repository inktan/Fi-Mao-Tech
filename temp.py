import os

def delete_files_by_split_count(folder_path, separator='_', target_count=10):
    """
    遍历文件夹，根据分隔符分割文件名，并删除符合数量条件的图片
    """
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff')
    
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return

    print(f"开始扫描文件夹: {folder_path}...")
    delete_count = 0

    for filename in os.listdir(folder_path):
        # 1. 检查是否为图片文件
        if filename.lower().endswith(image_extensions):
            # 2. 分离文件名和后缀（防止后缀中的点干扰分割）
            name_without_ext = os.path.splitext(filename)[0]
            
            # 3. 使用下划线分割
            elements = name_without_ext.split(separator)
            
            # 4. 判断分割后的元素数量
            if len(elements) == target_count:
                file_path = os.path.join(folder_path, filename)
                try:
                    # 执行删除
                    os.remove(file_path)
                    print(f"已删除: {filename} (元素数量: {len(elements)})")
                    delete_count += 1
                except Exception as e:
                    print(f"删除失败: {filename}, 错误: {e}")

    print("-" * 30)
    print(f"处理完成！共删除文件数量: {delete_count}")

# --- 使用示例 ---
# 请将下方的路径替换为你实际的文件夹路径
target_folder = r'F:\大数据\2025年8月份道路矢量数据\分城市的道路数据_50m_point_csv\泉州市\街景'
delete_files_by_split_count(target_folder)