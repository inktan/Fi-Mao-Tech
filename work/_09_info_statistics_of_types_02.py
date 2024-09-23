import os
import csv

def main(folder_path):
    # 指定文件夹路径

    # 统计文件夹中各个子文件夹所包含的文件数量
    file_counts = {}
    for root, dirs, files in os.walk(folder_path):
        count = 0
        for dir in dirs:
            dir_path = os.path.join(root, dir)

            with open(f'C:\\Users\\vipuser\\Desktop\\07-infol{dir}.csv','w' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['pic','patch','k-value'])

            for file_name in os.listdir(dir_path):
                file_name_info = file_name.split('_part_')
                info = [file_name_info[0]]
                info.append(file_name_info[1].split('.')[0])
                info.append(dir)

                with open(f'C:\\Users\\vipuser\\Desktop\\07-infol{dir}.csv','a' ,encoding='utf-8',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(info)

if __name__ == "__main__":
    folder_path =  r'c:\User\vipuser\Desktop\06-kemeans\kmeans_100'
    main(folder_path)
