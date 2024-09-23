# -*- coding: utf-8 -*-

import os
from PIL import Image

def del_file(folder_path):
    '''
    删除百度logo所在patch位置的瓦片
    '''
    baiduLocation = [(0, 3), (1, 3)] #百度logo所在patch位置 可自定义修改

    temp01 = f"_{baiduLocation[0][0]}_{baiduLocation[0][1]}"
    temp02 = f"_{baiduLocation[1][0]}_{baiduLocation[1][1]}"

    # 获取文件夹中的所有文件名
    file_names = os.listdir(folder_path)

    # 遍历所有文件名，删除包含指定字符串的文件
    for file_name in file_names:
        if temp01 in file_name or temp02 in file_name:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)

    print("删除logo结束")

def main():
    print('end')

if __name__ == "__main__":
    folder_path = ''
    del_file(folder_path)
