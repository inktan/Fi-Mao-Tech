import os
import subprocess

def download_public_folder(folder_id, output_path):
    """
    下载公开共享的Google Drive文件夹
    """
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    # 使用gdown命令行工具
    cmd = f"gdown --folder https://drive.google.com/drive/folders/{folder_id} -O {output_path}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("文件夹下载完成！")
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")

# 使用示例
folder_id = '1anv6zWAYY968TxRWAA570cHuAuXh0tlV'
output_path = './downloaded_folder'
download_public_folder(folder_id, output_path)