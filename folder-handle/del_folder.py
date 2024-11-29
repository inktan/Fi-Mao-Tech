import shutil  
import os  
  
folder_path = r'D:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_01_ss_rgb'  
  
if os.path.exists(folder_path):  
    shutil.rmtree(folder_path)  
    print(f"文件夹 '{folder_path}' 已成功删除。")
else:  
    print(f"文件夹 '{folder_path}' 不存在。")