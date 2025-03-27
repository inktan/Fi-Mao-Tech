import os

def count_files_in_directory(directory_path):
    """
    计算指定文件夹中的文件数量。

    :param directory_path: 文件夹的路径
    :return: 文件数量
    """
    return len([file for file in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, file))])

# 示例用法
directory_path = r'F:\work\Suzhou-SV-Ai'
print(count_files_in_directory(directory_path))
