import tarfile
import os
import glob

def extract_tar_files(pattern="*.tar"):
    tar_files = []
    for root, dirs, files in os.walk(r'g:\stree_view'):
        for file in files:
            if file.endswith('.tar'):
                full_path = os.path.join(root, file)
                tar_files.append(full_path)
    
    if not tar_files:
        print(f"未找到匹配 {pattern} 的tar文件")
        return
    
    print(f"找到 {len(tar_files)} 个tar文件")
    
    for tar_path in tar_files:
        try:
            print(f"正在解压: {tar_path}")
            
            # 确定解压目标路径
            target_dir = os.path.dirname(os.path.dirname(tar_path))
            
            # 使用with语句打开tar文件，确保正确关闭
            with tarfile.open(tar_path, 'r') as tar:
                # 解压到指定目录
                tar.extractall(path=target_dir)
            
            print(f"解压完成: {tar_path} -> {target_dir}")
            
            # 删除tar文件
            os.remove(tar_path)
            print(f"已删除: {tar_path}")
            
        except tarfile.TarError as e:
            print(f"解压失败 {tar_path}: {e}")
        except OSError as e:
            print(f"删除失败 {tar_path}: {e}")
        except Exception as e:
            print(f"处理 {tar_path} 时发生未知错误: {e}")

if __name__ == "__main__":
    # 使用方法示例：
    
    # 1. 解压当前目录下所有.tar文件
    extract_tar_files()
    
    # 2. 解压特定模式的tar文件
    # extract_tar_files("*.tar.gz")  # 解压.tar.gz文件
    # extract_tar_files("data_*.tar")  # 解压以data_开头的tar文件
    # extract_tar_files("/path/to/files/*.tar")  # 解压指定路径下的tar文件