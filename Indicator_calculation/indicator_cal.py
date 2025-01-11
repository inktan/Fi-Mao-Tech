# -*- coding: utf-8 -*-

import pandas as pd
import os
import csv
import math

import numpy as np
from PIL import Image
from tqdm import tqdm


def green_filter(image_grey_path,image_rgb_path,image_path):
    '''
    1、根据语义分析结果提取局部区域的图像，剔除部分使用纯白色填充
    2、计算色彩因子
    '''
    # 读取灰度图像  
    img_grey = np.array(Image.open(image_grey_path).convert('L'))  
    ss_rgb = np.array(Image.open(image_rgb_path))  
    img = np.array(Image.open(image_path))  
    
    # 查找像素值为4、17、9、66的索引位置  
    indices_1 = np.where((img_grey != 4) & (img_grey != 17) & (img_grey != 9) & (img_grey != 66))  
    ss_rgb[indices_1]=[0,0,0]
    img[indices_1]=[255,255,255]
    
    ss_rgb = Image.fromarray(ss_rgb)
    ss_rgb.save(image_rgb_path.replace("ss_rgb","ss_green_filter"))

    image = Image.fromarray(img)
    image.save(image_rgb_path.replace("ss_rgb","image_green_filter").replace("_ss.jpg",".jpg"))
    
    img[indices_1]=[0,0,0]
    rg = img[:,:, 0] - img[:,:, 1]
    yb = (img[:,:, 0] + img[:, :,1]) * 0.5 - img[:,:, 2]
    rg_lst = rg.flatten().tolist()  
    yb_lst = yb.flatten().tolist()

    rg_lst = [x for x in rg_lst if x != 0]  
    yb_lst = [x for x in yb_lst if x != 0]  

    std_dev_rg = np.std(rg_lst)  
    std_dev_yb = np.std(yb_lst)
    std_dev_rgvb = math.sqrt(std_dev_rg*std_dev_rg + std_dev_yb*std_dev_yb)

    mean_rg = np.mean(rg_lst)
    mean_yb = np.mean(rg_lst)
    mean_value_rgvb = math.sqrt(mean_rg*mean_rg + mean_yb*mean_yb)
  
    m_value=std_dev_rgvb + mean_value_rgvb*0.3
    
    return m_value
                
# 遍历文件夹中的文件
def main(image_ss_csv,Level_Diversity_csv):
    headers = ['id','p1-tree','p2-plant','p3-grass','p4-flower',\
                'Level_Diversity_richness', 'Level_Diversity_richness','Level_Diversity_entropy',\
                'TVF', 'GVI', 'H','H*(-1)', 'M', 'C', 'C*(-1)']

    with open('%s'%Level_Diversity_csv ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(headers)

    ss_data = pd.read_csv(image_ss_csv)
    length = len(ss_data)

    for i in tqdm(range(length)):
        if i<0:
            continue
        if i>10000:
            continue

        row = ss_data.loc[i]
        # 
        rate_list = []
        filename = row['id']
        # p1-tree p2-plant p3-grass p4-flower
        tree = row['tree']
        grass = row['plant;flora;plant;life']
        plant = row['grass']
        flower = row['flower']

        # richness
        Level_Diversity_richness = 0
        # entropy
        Level_Diversity_entropy = 0
        # simpson
        Level_Diversity_simpson = 0
        p_value = tree + plant + grass + flower
        
        # 'TVF'
        tvf = tree
        # 'GVI'
        gvi =  tree + grass + plant + flower
        # 视觉熵
        h_value = 0 
        
        # 'C'
        image_grey_path=os.path.join(r'D:\BaiduSyncdisk\FiMaoTech\Indicator_calculation\ss_grey',filename.replace(".jpg","_ss.png"))
        image_rgb_path=os.path.join(r'D:\BaiduSyncdisk\FiMaoTech\Indicator_calculation\ss_rgb',filename.replace(".jpg","_ss.jpg"))
        image_path=os.path.join(r'D:\BaiduSyncdisk\FiMaoTech\Indicator_calculation\1',filename)

        m_value = green_filter(image_grey_path,image_rgb_path,image_path)
        c_value = 0

        if tree != 0 :
            Level_Diversity_richness += 1
            Level_Diversity_entropy += tree* math.log2(tree)
            Level_Diversity_simpson += math.pow(tree/p_value, 2)

            h_value +=  tree* math.log10(tree)
            c_value = m_value*tree* math.log10(tree)
        if plant != 0 :
            Level_Diversity_richness += 1
            Level_Diversity_entropy += plant* math.log2(plant)
            Level_Diversity_simpson += math.pow(plant/p_value, 2)

            h_value +=  plant* math.log10(plant)
            c_value = m_value*plant* math.log10(plant)

        if grass != 0 :
            Level_Diversity_richness += 1
            Level_Diversity_entropy += grass* math.log2(grass)
            Level_Diversity_simpson += math.pow(grass/p_value, 2)

            h_value +=  grass* math.log10(grass)
            c_value = m_value*grass* math.log10(grass)

        if flower != 0 :
            Level_Diversity_richness += 1
            Level_Diversity_entropy += flower* math.log2(flower)
            Level_Diversity_simpson += math.pow(flower/p_value, 2)

            h_value +=  flower* math.log10(flower)
            c_value = m_value*flower* math.log10(flower)

        
        Level_Diversity_entropy *= -1
        Level_Diversity_simpson = 1 - Level_Diversity_simpson

        # to csv
        rate_list.append(filename)
        rate_list.append(tree)
        rate_list.append(plant)
        rate_list.append(grass)
        rate_list.append(flower)

        rate_list.append(Level_Diversity_richness)
        rate_list.append(Level_Diversity_entropy)
        rate_list.append(Level_Diversity_simpson)

        rate_list.append(tvf)
        rate_list.append(gvi)

        rate_list.append(h_value)
        rate_list.append(h_value*(-1))
        rate_list.append(m_value)
        rate_list.append(c_value)
        rate_list.append(c_value*(-1))

        with open('%s' % Level_Diversity_csv ,'a' ,newline='') as f:
            writer = csv.writer(f)
            writer.writerow(rate_list)

if __name__ == "__main__":
    image_ss_csv = os.path.join(r"D:\BaiduSyncdisk\FiMaoTech\Indicator_calculation","ss_result.csv")
    Level_Diversity_csv = os.path.join(r"D:\BaiduSyncdisk\FiMaoTech\Indicator_calculation",'Level_Diversity.csv')

    main(image_ss_csv,Level_Diversity_csv)
    

