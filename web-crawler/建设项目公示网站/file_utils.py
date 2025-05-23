import os
import re
def get_deepest_dirs(root_dir):
    """获取所有嵌套最底层的文件夹路径（没有子文件夹的文件夹）"""
    deepest_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if not dirnames:  # 如果没有子文件夹，说明是底层文件夹
            dir_name = os.path.basename(dirpath)  # 获取文件夹名（不含路径）
            deepest_dirs.add(dir_name)

    return deepest_dirs


def create_safe_dirname(project_name, publish_date):
    """创建安全的文件夹名称"""
    # 移除特殊字符
    project_name = re.sub(r'[\\/*?:"<>|]', "", project_name)
    publish_date = re.sub(r'[\\/*?:"<>|]', "", publish_date)
    # 合并为文件夹名
    dirname = f"{project_name}_{publish_date[:10]}"  # 只取日期部分
    return dirname[:100]  # 限制长度防止路径过长