# -*- coding: utf-8 -*-

from sklearn import cluster
import os
from tqdm import tqdm
import csv
from PIL import Image
import numpy as np
from scipy.spatial import distance
import matplotlib.pylab as plt
import matplotlib.cm as cm

def folder_exists(folderPath):
    if os.path.exists(folderPath) == False:
        os.mkdir(folderPath)
        print("The folder was created successfully ==>" + folderPath)
    else:
        print('The folder already exists ==>' + folderPath)

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

def getPixData(img_path):
    image = Image.open(img_path)
    pixels = np.array(image)
    pixData = pixels.reshape(pixels.shape[0] * pixels.shape[1], -1)
    pixData = [row for row in pixData if int(row[0])+int(row[1])+int(row[2]) < 759]

    # for i in pixData:
    #     value_ =i[0] + i[1] + i[2]
    #     if value_>758:
    #         print(i)

    return pixData

def classify_pixels(image_path, colors):
    image = Image.open(image_path)
    pixels = np.array(image)
    height, width, _ = pixels.shape
    pixels = pixels.reshape(height * width, -1)
    pixels = np.array([np.array(row) for row in pixels if list(row) != [255, 255, 255]])
    dist_matrix = distance.cdist(pixels, colors)
    closest_indices = np.argmin(dist_matrix, axis=1)
    color_counts = np.bincount(closest_indices, minlength=len(colors))
    color_ratios = color_counts /  pixels.shape[0] 
    return color_ratios

def color_range(image_path):
    image = Image.open(image_path)
    pixels = np.array(image)
    height, width, _ = pixels.shape
    min_value = 0
    max_value = 16777215
    interval = (max_value - min_value) // 8
    counts = [0] * 8
    for y in range(height):
        for x in range(width):
            r, g, b = image.getpixel((x, y))
            if r==255 and g==255 and b==255:
                continue
            hex_value = (r << 16) + (g << 8) + b
            index = (hex_value - min_value) // interval
            if index>=8:
                index=7
            counts[index] += 1
    return counts

def cityColorThemes(imgPaths,imgNames,folder_out_path):
    for i, img_path in enumerate(tqdm(imgPaths)):
        if i<=3900:
            continue
        # if i>5200:
        #     continue

        pix_data = getPixData(img_path)
        km=cluster.KMeans(n_clusters=8)
        try:
            km.fit(pix_data)
        except:
            continue

        quantize=np.array(km.cluster_centers_, dtype=np.uint8) 
        ratios = classify_pixels(img_path, quantize.tolist())
        show_cityColor_impression(img_path,imgNames[i],quantize,ratios,folder_out_path)
        quantize_csv = [imgNames[i]] 
        dict_hsv_ration = {tuple(rgb2hsv(key)): value for key, value in zip(quantize, ratios)} 
        dict_hsv_ration = dict(sorted(dict_hsv_ration.items(), key=lambda item: item[1], reverse=True)) 
        quantize_csv.extend(dict_hsv_ration.keys())
        quantize_csv.extend(dict_hsv_ration.values())

        with open(r'F:\build\color_cal_.csv','a' ,newline='') as f:
            writer = csv.writer(f)
            try:
                writer.writerow(quantize_csv)
            except:
                print()
    return
    
def show_cityColor_impression(image_path,imgName,quantize,ratios,folder_out_path):
    fig = plt.figure(figsize=(28, 5))
    grid = plt.GridSpec(1, 2, hspace=0, wspace=0,width_ratios=[9,1])
    ax3 = fig.add_subplot(grid[0, 0])
    image = Image.open(image_path)  
    image_np = np.array(image)  
    ax3.imshow(image_np)
    ax3.axis('off')

    ax4 = fig.add_subplot(grid[0, 1])
    colors=[tuple(i) for i in quantize]
    colors = ['#%02x%02x%02x' % rgb for rgb in colors]
    rects3 = ax4.barh(range(len(quantize)), ratios, height=0.6,color=colors)
    ax4.yaxis.set_ticks([])
    ax4.set_xlim(0, 1.0)
    ax4.set_title('')
    ax4.bar_label(rects3, padding=0, labels=[f'{x*100:.0f}%' for x in ratios], color="r",fontsize=10)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['left'].set_visible(False)
    ax4.set_anchor('W')
    index = imgName.rfind('.')
    plt.savefig(folder_out_path+'\\'+imgName[:index]+'_color_plot.png')
    plt.close('all')
    
if __name__ == "__main__":
    
    # 文件夹路径
    folder_path = r'F:\build\sv_arch_merge' # 需要分析的文件夹路径
    folder_out_path = r'F:\build\build_out' # 保存文件结果的文件夹路径
    
    folder_exists(folder_out_path)
    img_paths = []
    img_names = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png") or file.endswith(".jpeg"):
                file_path = os.path.join(root, file)
                img_paths.append(file_path)
                img_names.append(file)

    # with open(r'F:\build\color_cal_.csv','w' ,newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["File_Name",\
    #                      "Color_tone_1","Color_tone_2","Color_tone_3","Color_tone_4","Color_tone_5","Color_tone_6","Color_tone_7","Color_tone_8",\
    #                      "Percentage_1","Percentage_2","Percentage_3","Percentage_4","Percentage_5","Percentage_6","Percentage_7","Percentage_8",
    #                     ])
 
    cityColorThemes(img_paths, img_names,folder_out_path)