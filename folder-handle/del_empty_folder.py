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

# 使用示例
if __name__ == "__main__":
    folder_path = r'E:'
    if os.path.isdir(folder_path):
        remove_empty_folders(folder_path)
        print("操作完成")
    else:
        print("指定的路径不是一个有效的文件夹")