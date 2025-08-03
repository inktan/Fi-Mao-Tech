# _*_ coding: utf-8 _*_
import cv2
import os
import math
import sys
import numpy as np

root_dir = r'e:\work\sv_huang_g\半球_fisheye'
image_types = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
img_paths = []

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.lower().endswith(image_types):
            file_path = os.path.join(root, file)
            img_paths.append(file_path)

# 开始处理图片
for inputimg in img_paths:
    # fisheye_img = cv2.imread(inputimg)
    fisheye_img = cv2.imdecode(np.fromfile(inputimg, dtype=np.uint8), cv2.IMREAD_COLOR)
    r = 82

    # 缩放至173x173尺寸
    fisheye_img = cv2.resize(fisheye_img, (173, 173), interpolation=cv2.INTER_LINEAR)
    svf = 0.00 #天空占比
    tvf = 0.00 #植物占比
    for index in range(1,28):
        circled_img = cv2.imdecode(np.fromfile(inputimg, dtype=np.uint8), cv2.IMREAD_COLOR)
        circled_img = cv2.resize(fisheye_img, (173, 173), interpolation=cv2.INTER_LINEAR)
        #print('正在计算'+inputimg+'的第',index,'圈,共27圈')
        cv2.circle(circled_img,(86,86),r,[0,255,255])
        cv2.circle(circled_img,(86,86),r-1,[0,255,255])
        cv2.circle(circled_img,(86,86),r-2,[0,255,255])
        circle_points = []
        sky_points = []
        tree_points = []
        for i in range(0, 173):
            for j in range(0, 173):
                if circled_img[i][j][0] == 0 and circled_img[i][j][1] == 255 and circled_img[i][j][2] == 255:
                    circle_points.append([i,j])
        #计算天空,植物，建筑占比
        for point in circle_points:
            x= point[0]
            y= point[1]
            if fisheye_img[x][y][2] in range(0,10) and fisheye_img[x][y][1] in range(220,240) and fisheye_img[x][y][0] in range(220,240):
                #fisheye_img[x][y] =[0,255,255]
                sky_points.append(point)
            # elif fisheye_img[x][y][0] in range(0,200) and fisheye_img[x][y][1] in range(170,256) and fisheye_img[x][y][2] in range(0,200):
                #fisheye_img[x][y] = [255, 0, 0]
                # tree_points.append(point)

        #cv2.imshow("Display window", fisheye_img)
        #cv2.waitKey(0)
        #天空占比
        #print('总像素', len(circle_points), '个')
        sky = len(sky_points)/len(circle_points)
        #print('天空像素',len(sky_points),'个,占比为',sky)
        svf += math.sin(math.pi*(2*index-1)/54)*sky
        #植物占比
        # tree = len(tree_points)/len(circle_points)
        #print('植物像素',len(tree_points),'个,占比为',tree)
        # tvf = tvf + math.sin(math.pi*(2*index-1)/54)*tree

        r=r-3
    svf = (math.pi/54) * svf
    # tvf = (math.pi/54) * tvf
    print(inputimg + '的结果计算完毕','天空占比为', svf)
