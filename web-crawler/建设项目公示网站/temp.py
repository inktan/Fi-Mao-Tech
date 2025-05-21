import os

def get_deepest_dirs(root_dir):
    """获取所有嵌套最底层的文件夹路径（没有子文件夹的文件夹）"""
    deepest_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # 如果没有子文件夹，说明是底层文件夹
            dir_name = os.path.basename(dirpath)  # 获取文件夹名（不含路径）
            deepest_dirs.add(dir_name)

    return deepest_dirs

# 示例：遍历当前目录下的所有文件夹
root_directory = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\上海市"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

# 打印所有底层文件夹名
print("所有底层文件夹名：", deepest_dir_names)

# 判断一个字符串是否不在集合中
target = r"Y:\GOA-项目公示数据\建设项目公示信息\上海\上海市"  # 替换为你要判断的字符串
if target not in deepest_dir_names:
    print(f"'{target}' 不在最底层文件夹集合中")
else:
    print(f"'{target}' 在最底层文件夹集合中")