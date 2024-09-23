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

            with open(f'E:\sv\work\sv\07-info\{dir}.csv','w' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['pic','lat','lng','patch','k-value'])

            for file_name in os.listdir(dir_path):
                part = file_name.split('-')
                info = part[0].split('_')
                info.append(part[1].split('.')[0])
                info.append(dir)

                if len(info) != 6:
                    continue

                if float(info[0]) >0 and float(info[1]) >0 and float(info[2]) >0 :
                    with open(f'E:\sv\work\sv\07-info\{dir}.csv','a' ,encoding='utf-8',newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(info)

if __name__ == "__main__":
    folder_path = r'E:\sv\work\sv\06-kmeans\kmeans_100'
    main(folder_path)
