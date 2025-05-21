import os

def remove_empty_folders(path):
    """
    递归删除空文件夹
    :param path: 要检查的文件夹路径
    :return: True如果文件夹为空并被删除，False如果文件夹不为空
    """
    if not os.path.isdir(path):
        return False
    
    # 检查文件夹是否为空
    if not os.listdir(path):
        try:
            os.rmdir(path)
            print(f"已删除空文件夹: {path}")
            return True
        except OSError as e:
            print(f"删除文件夹 {path} 失败: {e}")
            return False
    
    # 递归检查子文件夹
    has_empty = False
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            if remove_empty_folders(item_path):
                has_empty = True
    
    # 如果子文件夹被删除后当前文件夹变为空，则再次尝试删除
    if has_empty and not os.listdir(path):
        try:
            os.rmdir(path)
            print(f"子文件夹删除后，已删除空文件夹: {path}")
            return True
        except OSError as e:
            print(f"删除文件夹 {path} 失败: {e}")
            return False
    
    return False

import os
import shutil

def find_and_remove_expired_folders(root_dir, keyword="公示已到期"):
    """
    查找并删除嵌套最底层且名称包含关键字的文件夹
    
    :param root_dir: 要搜索的根目录
    :param keyword: 要匹配的关键词(默认"公示已到期")
    """
    for root, dirs, files in os.walk(root_dir, topdown=False):
        # topdown=False 表示自底向上遍历，先处理子目录再处理父目录
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            
            # 检查是否是底层文件夹(没有子文件夹)
            is_bottom_level = True
            for _, sub_dirs, _ in os.walk(dir_path):
                if sub_dirs:  # 如果有子文件夹，则不是底层
                    is_bottom_level = False
                    break
            
            # 如果是底层文件夹且名称包含关键词
            if is_bottom_level and keyword in dir_name:
                try:
                    print(f"删除文件夹: {dir_path}")
                    shutil.rmtree(dir_path)  # 删除整个文件夹及其内容
                except Exception as e:
                    print(f"删除失败 {dir_path}: {e}")
            if is_bottom_level and '住宅加装电梯' in dir_name:
                try:
                    print(f"删除文件夹: {dir_path}")
                    shutil.rmtree(dir_path)  # 删除整个文件夹及其内容
                except Exception as e:
                    print(f"删除失败 {dir_path}: {e}")

# 使用示例
if __name__ == "__main__":
    folder_path = r'Y:\GOA-项目公示数据\建设项目公示信息'
    find_and_remove_expired_folders(folder_path)

    if os.path.isdir(folder_path):
        remove_empty_folders(folder_path)
        print("操作完成")
    else:
        print("指定的路径不是一个有效的文件夹")