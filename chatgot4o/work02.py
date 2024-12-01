from tqdm import tqdm
import os
import re
import os
import shutil
import csv

def main(img_folder,csv_path):
    headers=['id','score']
    with open('%s'%csv_path ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(headers)

    roots = []
    img_names = []
    img_paths = []
    accepted_formats = (".txt")
    for root, dirs, files in os.walk(img_folder):
        for file in files:
            if file.endswith(accepted_formats):
                roots.append(root)
                img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    for i, img_path in enumerate(tqdm(img_paths)):
        # src = img_path.replace('.txt', '.jpg').replace('txt_01', 'test')
        # dst = img_folder.replace('txt_01', 'test01')
        # shutil.move(src, dst)
        # continue


        # 打开文件
        with open(img_path, 'r',encoding='utf-8') as file:
            lines = file.readlines()

        # 删除最后一行
        # if lines:
        #     lines.pop()
    
        numbers = []
        for line in lines:
            numbers.extend(re.findall(r'-?\d+\.?\d*', line))

        numbers = [ s for s in numbers if '.' in s] 

        rate_list=[img_names[i],3]
        if numbers:
            last_number = numbers[-1]
            rate_list=[img_names[i],last_number]

            # if isinstance(last_number, float):
            #     rate_list=[img_names[i],last_number]
            # else:
            #     last_number = numbers[-2]
            #     rate_list=[img_names[i],last_number]

            # 将结果写入csv
        with open('%s' % csv_path ,'a',encoding='utf-8' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rate_list)

if __name__ == '__main__':
    img_folder = r'E:\work\spatio_evo_urbanvisenv_svi\风貌评估-gpt4o\拉萨市传统商业街区街景\txt_01'
    csv_path= os.path.join(r'E:\work\spatio_evo_urbanvisenv_svi\风貌评估-gpt4o\拉萨市传统商业街区街景',"txt.csv")
    main(img_folder,csv_path)

    # 检查文件夹是否存在
    # if os.path.exists(img_folder):
    #     # 删除文件夹及其所有内容
    #     shutil.rmtree(img_folder)
    #     print(f'文件夹"{img_folder}"已删除。')
    # else:
    #     print(f'文件夹"{img_folder}"不存在。')
