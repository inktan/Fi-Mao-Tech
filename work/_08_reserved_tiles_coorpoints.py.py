import csv  
from tqdm import tqdm
import os 

csv_01 = 'F:\sv\补充\SVI_SS.csv'
csv_02 ='F:\sv\补充\Patch_SS_filter_result.csv'

# 所有过滤后保存的瓦片文件
all_file_names = os.listdir(r'F:\sv\street-view-patch-filter-1955')  

file_collection = []

with open(csv_01, 'r') as csv_file:  
    reader = csv.reader(csv_file)  
    # print(len(list(reader)))
    for i, row in enumerate(tqdm(reader)):
        if i==0:
            header = ['pic', 'lat', 'lng', 'patch','filter','reject']
            with open('%s' % csv_02 ,'w' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
        else:
            image_name = row[0] + '_' + row[1] + '_' + row[2]

            if image_name not in file_collection:
                file_collection.append(image_name)
            else:
                continue

            count = sum(1 for string in all_file_names if image_name in string)  

            new_row = [row[0]]
            new_row.append(row[1])  
            new_row.append(row[2])  
            new_row.append(n)  
            new_row.append(count)  
            new_row.append(64-count)  
   
            with open('%s' % csv_02 ,'a' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(new_row)
