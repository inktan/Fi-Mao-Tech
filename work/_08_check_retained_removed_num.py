import csv  
from tqdm import tqdm
import os 
def main(image_fold,ss_csv,info_csv,n):
    # 所有过滤后保存的瓦片文件
    all_file_names = os.listdir(image_fold)  
    file_collection = []
    with open(ss_csv, 'r') as csv_file:  
        reader = csv.reader(csv_file)  
        # print(len(list(reader)))
        for i, row in enumerate(tqdm(reader)):
            if i==0:
                header = ['pic', 'lat', 'lng', 'patch','filter','reject']
                with open('%s' % info_csv ,'w' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
            else:
                # image_name = row[0] + '_' + row[1] + '_' + row[2]
                image_name = row[0].split('.')[0]
                if image_name not in file_collection:
                    file_collection.append(image_name)
                else:
                    continue

              
                all_iamge_names =[i.split('_')[0] for i in  all_file_names]
                count = all_iamge_names.count(image_name) 

                new_row = [row[0]]
                new_row.append(row[1])  
                new_row.append(row[2])  
                new_row.append(n)  
                new_row.append(count)  
                new_row.append(n-count)  
    
                with open('%s' % info_csv ,'a' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(new_row)

if __name__ == "__main__":
    # 输入保留瓦片数据集
    image_fold = r'D:\BaiduSyncdisk\FiMaoTech\Optimization_SV_Classification\work\sv\05-filter\img-filter'
    # 输入⚪街景文件的语义分析结果
    ss_csv = 'sv/02-ss/ss_result.csv'
    # 保存每个原街景点，保留与剔除的瓦片数量
    info_csv = r'D:\BaiduSyncdisk\FiMaoTech\Optimization_SV_Classification\work\sv\07-info\check_retained_removed_num.csv'
    # 一个街景分割成的总瓦片数量
    n=64
    main(image_fold,ss_csv,info_csv,n)
