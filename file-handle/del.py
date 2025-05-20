import os

def delete_attachment_files(folder_path):
    """
    递归删除文件夹中所有名为 'attachment' 的文件
    :param folder_path: 要搜索的文件夹路径
    """
    deleted_count = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 检查文件名是否是 'attachment'（不区分大小写）
            if file.lower() == 'attachment':
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"已删除文件: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除文件 {file_path} 失败: {e}")
    
    print(f"\n操作完成，共删除 {deleted_count} 个名为 'attachment' 的文件")

# 使用示例
if __name__ == "__main__":
    target_folder = r'Y:\GOA-项目公示数据\建设项目公示信息'
    delete_attachment_files(target_folder)