import glob
import os

# 指定要检查的文件夹路径
folder_path = r'F:\sv_hangzhou\hangzhou_800_600_108776'

for i in range(1, 107000):
    pattern = os.path.join(folder_path, str(i)+'_' + '*')
    if len(glob.glob(pattern))>4:
        print(i)

