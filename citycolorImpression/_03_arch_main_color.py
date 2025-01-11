# -*- coding: utf-8 -*-

from sklearn import cluster
import os
from tqdm import tqdm 
import csv
from PIL import Image
import numpy as np
from scipy.spatial import distance
import matplotlib.pylab as plt
import matplotlib.image as mpimg  
import matplotlib.cm as cm
import math

def rgb2hsv(rgb):
    '''
    RGB转HSV
    r,g,b在(0-255)
    '''
    r, g, b = rgb[0], rgb[1], rgb[2]
    r, g, b = r/255.0, g/255.0, b/255.0
    mx, mn = max(r, g, b), min(r, g, b)
    m = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        if g >= b:
            h = ((g-b)/m)*60
        else:
            h = ((g-b)/m)*60 + 360
    elif mx == g:
        h = ((b-r)/m)*60 + 120
    elif mx == b:
        h = ((r-g)/m)*60 + 240
    if mx == 0:
        s = 0
    else:
        s = m/mx
    v = mx
    return (h, s, v)
def hsv2rgb(hsv):
    '''
    HSV转RGB
    注意, h在(0-360), s,v在(0-1)
    '''
    h, s, v = map(float, (hsv[0], hsv[1], hsv[2]))
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return (r, g, b)

def classify_pixels(pixels, colors):
    dist_matrix = distance.cdist(pixels, colors)
    closest_indices = np.argmin(dist_matrix, axis=1)
    color_counts = np.bincount(closest_indices, minlength=len(colors))
    color_ratios = color_counts /  len(pixels)
    return color_ratios

def cityColorThemes(imgPaths,imgNames,image_ss_csv):
    for i,img_path in enumerate( tqdm(imgPaths)):
        # print(i)
        # if i > 10000:
        #     continue
        image = Image.open(img_path)
        pixels = np.array(image)

        pixData = pixels.reshape(pixels.shape[0] * pixels.shape[1], -1).tolist()
        pixData = [row for row in pixData if row[0] + row[1] + row[2] <760]
        
        if len(pixData) == 0:
            continue

        km=cluster.KMeans(n_init=8)
        try:
            km.fit(pixData)
        except:
            continue

        rgb_list=np.array(km.cluster_centers_, dtype=np.uint8) 
        ratios = classify_pixels(pixData, rgb_list.tolist())
        
        dict_hsv_ration = {tuple(rgb2hsv(key)): value for key, value in zip(rgb_list, ratios)} 

        dict_hsv_ration = dict(sorted(dict_hsv_ration.items(), key=lambda item: item[1], reverse=True)) 
        quantize_csv = [imgNames[i]]

        quantize_csv.extend(dict_hsv_ration.keys())
        quantize_csv.extend(dict_hsv_ration.values())

        with open(image_ss_csv,'a' ,newline='') as f:
            writer = csv.writer(f)
            try:
                writer.writerow(quantize_csv)
            except:
                print()
        show_cityColor_impression(img_path,rgb_list,ratios)
        image = None

    return
def show_cityColor_impression(img_path,colors,ratios):
    fig = plt.figure(figsize=(9, 5))
    grid = plt.GridSpec(1, 2, hspace=0, wspace=0,width_ratios=[1, 0.2])
    ax3 = fig.add_subplot(grid[0, 0])
    ax3.imshow(mpimg.imread(img_path))
    ax3.axis('off')
    ax4 = fig.add_subplot(grid[0, 1])
    colors=[tuple(i) for i in colors]
    colors = ['#%02x%02x%02x' % rgb for rgb in colors]
    rects3 = ax4.barh(range(len(colors)), ratios, height=0.6,color=colors)
    ax4.yaxis.set_ticks([])
    ax4.set_xlim(0, 1.0)
    ax4.set_title('')
    ax4.bar_label(rects3, padding=0, labels=[f'{x*100:.0f}%' for x in ratios], color="r",fontsize=10)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_visible(False)
    ax4.set_anchor('W')

    tmp = img_path.replace('sv_pan_01','color_analy')
    folder_path = os.path.dirname(tmp)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    if ".jpg" in tmp:
        tmp = tmp.replace(".jpg",".png")
    elif ".jpeg" in tmp:
        tmp = tmp.replace(".jpeg",".png")
    elif ".JPG" in tmp:
        tmp = tmp.replace(".JPG",".png")

    plt.savefig(tmp)

    plt.close('all')
if __name__ == "__main__":
    
    # 文件夹路径
    folder_path = r'E:\work\sv_123\sv_pan_01' # 需要分析的文件夹路径
    image_ss_csv = r'E:\work\sv_123\main_color_sv_pan_color.csv'
        
    img_paths = []
    img_names = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)

    with open(image_ss_csv,'w' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["File_Name","Color_1","Color_2","Color_3","Color_4","Color_5","Color_6","Color_7","Color_8",\
                         "Percentage_1","Percentage_2","Percentage_3","Percentage_4","Percentage_5","Percentage_6","Percentage_7","Percentage_8"])
 
    cityColorThemes(img_paths, img_names, image_ss_csv)


    