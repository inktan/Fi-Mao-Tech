import tarfile
import os
import glob
import subprocess

def extract_tar_files(pattern="*.tar"):
    tar_files = []
    for root, dirs, files in os.walk(r'e:\stree_view'):
        if 'sv_pano' in root:
            continue
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
            if tar_path.endswith(r'01.tar'):
                continue
            if tar_path.endswith(r'02.tar'):
                continue
            
            # 确定解压目标路径
            target_dir = os.path.dirname(os.path.dirname(tar_path))
            
            bandizip_path = r'c:\Program Files\Bandizip\Bandizip.exe'  # 根据实际安装路径调整
            output_dir = r'e:\stree_view'
            # for tar_file in tar_files:
            cmd = [
                bandizip_path,
                'x',           # 解压命令
                tar_path,      # 要解压的文件
                f'-o:{output_dir}',  # 输出目录
                '-y',          # 全部选择是（自动确认）
                '-aoa',        # 覆盖模式：直接覆盖所有现有文件
                '-spe',        # 从压缩文件中排除根文件夹
                '-p:',         # 如果没有密码，使用空密码参数
                '-hide'        # 隐藏Bandizip界面（关键参数）
            ]
            
            # 启动解压进程
            process = subprocess.Popen(cmd,
                                    creationflags=subprocess.CREATE_NO_WINDOW,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            
            # 等待进程完成
            process.wait()
            
            # 确保所有Bandizip进程都被关闭
            subprocess.run(['taskkill', '/f', '/im', r'c:\Program Files\Bandizip\Bandizip.exe', '/t'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
            
            # 使用with语句打开tar文件，确保正确关闭
            # with tarfile.open(tar_path, 'r') as tar:
                # 解压到指定目录
                # tar.extractall(path=r'e:\stree_view')
            
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