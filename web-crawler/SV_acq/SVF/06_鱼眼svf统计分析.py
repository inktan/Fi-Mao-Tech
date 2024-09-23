    # -*- coding:utf-8 -*-


import os
import csv
from PIL import Image
import numpy as np



in_rootdir=r"C:\Users\Administrator\Desktop\新建文件夹 (4)"       #街景分割结果保存文件夹
out_file=r"F:\streetview\nju4\鱼眼roadsvf结果汇总统计zz.csv"     #汇总统计结果保存路径



count=0
writer=csv.writer(open(out_file,"w",newline=""),dialect =("excel"))
writer.writerow(["pid","road","sidewalk","building","wall","fence",
                 "pole","traffic_light","traffic_sign","vegetation","terrain",
                 "sky","person","rider","car","truck","bus","train","motorcycle","bicycle"])
for filen in os.listdir(in_rootdir):
    img=Image.open(os.path.join(in_rootdir,filen))
    count+=1
    count_dic = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0,
                 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, -1: 0, 255: 0}
    ar = np.array(img).flatten().tolist()
    for item in count_dic:
        count_dic[item]=ar.count(item)
    sumcount=83469
    writer.writerow([filen.split(".")[0],count_dic[0]*1.0/sumcount,count_dic[1]*1.0/sumcount,count_dic[2]*1.0/sumcount,
                     count_dic[3]*1.0/sumcount,count_dic[4] * 1.0 / sumcount,count_dic[5]*1.0/sumcount,
                     count_dic[6]*1.0/sumcount,count_dic[7]*1.0/sumcount,count_dic[8] * 1.0 / sumcount,
                     count_dic[9]*1.0/sumcount,count_dic[10]*1.0/sumcount,count_dic[11]*1.0/sumcount,
                     count_dic[12]*1.0/sumcount,count_dic[13] * 1.0 / sumcount,count_dic[14]*1.0/sumcount,
                     count_dic[15]*1.0/sumcount,count_dic[16]*1.0/sumcount,count_dic[17]*1.0/sumcount,
                     count_dic[18]*1.0/sumcount])
    print(filen,count)

