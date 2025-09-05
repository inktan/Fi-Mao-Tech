import tarfile
import os
import glob
import concurrent.futures
import gzip
import shutil

def extract_tar_gz_optimized(tar_file_path):
    """
    优化的解压方法，先解压.gz，再解压.tar
    """
    try:
        # 创建解压目录
        base_name = os.path.splitext(os.path.splitext(tar_file_path)[0])[0]
        extract_dir = base_name
        os.makedirs(extract_dir, exist_ok=True)
        
        # 先解压.gz，再解压.tar（有时比直接解压.tar.gz更快）
        temp_tar_path = tar_file_path[:-3]  # 去掉.gz
        
        # 解压.gz文件
        with gzip.open(tar_file_path, 'rb') as gz_file:
            with open(temp_tar_path, 'wb') as tar_file:
                shutil.copyfileobj(gz_file, tar_file)
        
        # 解压.tar文件
        with tarfile.open(temp_tar_path, 'r') as tar:
            tar.extractall(path=extract_dir)
        
        # 删除临时文件
        os.remove(temp_tar_path)
        
        return f"成功解压: {os.path.basename(tar_file_path)}"
        
    except Exception as e:
        return f"解压失败 {os.path.basename(tar_file_path)}: {e}"

def fast_extract_all(directory):
    """
    最高效的解压实现
    """
    import multiprocessing
    
    # 获取所有.tar.gz文件
    tar_files = glob.glob(os.path.join(directory, "*.tar.gz"))
    
    if not tar_files:
        print("未找到.tar.gz文件")
        return
    
    print(f"开始解压 {len(tar_files)} 个文件...")
    
    # 使用进程池（对于CPU密集型任务，进程比线程更高效）
    cpu_count = multiprocessing.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count) as executor:
        results = list(executor.map(extract_tar_gz_optimized, tar_files))
    
    # 打印结果
    for result in results:
        print(result)

# 简单调用
if __name__ == "__main__":
    target_dir = r"E:\stree_view\work01"
    
    if os.path.exists(target_dir):
        fast_extract_all(target_dir)
    else:
        print(f"目录不存在: {target_dir}")