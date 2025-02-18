import os

def count_files_in_subdirectories(directory):
    # 获取一级子目录
    subdirectories = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
    
    # 遍历每个子目录并统计文件数量
    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)
        files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
        if len(files) > 0:
            print(f"Folder: {subdir_path}, Number of files: {len(files)}")

if __name__ == "__main__":
    # 指定要搜索的目录，默认为当前目录
    start_directory = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\街道分类\sv_山南点位\sv_pan'
    count_files_in_subdirectories(start_directory)