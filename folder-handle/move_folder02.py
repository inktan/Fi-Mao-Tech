import os
import shutil

def move_folders_to_parent(source_path):
    """
    将指定路径下的所有文件夹移动到上一级目录，遇到同名文件夹时进行内容合并
    
    Args:
        source_path (str): 源目录路径
    """
    # 检查源目录是否存在
    if not os.path.exists(source_path):
        print(f"源目录不存在: {source_path}")
        return
    
    # 获取上一级目录路径
    parent_path = r'g:\stree_view'
    
    # 获取源目录下的所有项目
    items = os.listdir(source_path)
    
    # 筛选出文件夹（排除文件）
    folders = [item for item in items if os.path.isdir(os.path.join(source_path, item))]
    
    if not folders:
        print(f"在目录 {source_path} 中没有找到文件夹")
        return
    
    print(f"找到 {len(folders)} 个文件夹需要移动/合并")
    
    # 移动/合并每个文件夹
    processed_count = 0
    for folder_name in folders:
        try:
            source_folder = os.path.join(source_path, folder_name)
            target_folder = os.path.join(parent_path, folder_name)
            
            # 如果目标位置不存在同名文件夹，直接移动
            if not os.path.exists(target_folder):
                shutil.move(source_folder, target_folder)
                print(f"已移动: {folder_name}")
            else:
                # 如果目标位置已存在同名文件夹，合并内容
                merge_folders(source_folder, target_folder)
                # 删除源文件夹（因为内容已经合并）
                shutil.rmtree(source_folder)
                print(f"已合并: {folder_name}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"处理文件夹 {folder_name} 时出错: {e}")
    
    print(f"处理完成！成功处理了 {processed_count} 个文件夹")

def merge_folders(source_dir, target_dir):
    """
    将源文件夹的内容合并到目标文件夹中，同名文件会被覆盖
    
    Args:
        source_dir (str): 源文件夹路径
        target_dir (str): 目标文件夹路径
    """
    # 确保目标文件夹存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 遍历源文件夹中的所有内容
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        target_item = os.path.join(target_dir, item)
        
        # 如果是文件夹，递归合并
        if os.path.isdir(source_item):
            if os.path.exists(target_item) and os.path.isdir(target_item):
                # 如果目标位置存在同名文件夹，递归合并
                merge_folders(source_item, target_item)
            else:
                # 如果目标位置不存在或不是文件夹，直接移动
                shutil.move(source_item, target_item)
        else:
            # 如果是文件，直接覆盖（如果存在）
            if os.path.exists(target_item):
                os.remove(target_item)  # 先删除目标文件
            shutil.move(source_item, target_item)

# 使用示例
if __name__ == "__main__":
    # 指定源目录路径
    source_directory = r"E:\stree_view\tar_08815"
    
    move_folders_to_parent(source_directory)
    
    
    
    