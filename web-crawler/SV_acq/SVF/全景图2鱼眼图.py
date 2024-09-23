# -*- coding: utf-8 -*-
"""
Created on  2018.6.30

@author: 非猫科技

opencv函数
cv2.getRectSubPix() 从图像中提取象素矩形，使用子象素精度
https://blog.csdn.net/qq_37385726/article/details/82314116

cv2.circle() 根据给定的圆心和半径等画圆
https://blog.csdn.net/viven_hui/article/details/102807995

cv2.bitwise_and() 二进制数据进行“与”操作，即对图像（灰度图像或彩色图像均可）每个像素值进行二进制“与”操作利用掩膜（mask）进行“与”操作，即掩膜图像白色区域是对需要处理图像像素的保留，黑色区域是对需要处理图像像素的剔除，其余按位操作原理类似只是效果不同而已。
https://www.jb51.net/article/189062.htm

cv2.getRotationMatrix2D(获得仿射变化矩阵)
cv2.warpAffine(进行仿射变化)
https://www.icode9.com/content-4-438109.html
"""
import cv2
import numpy as np
import math
from math import pi,atan

#创建鱼眼
# 鱼眼的半径r=width/2PI。街景分辨率为1024*256，则鱼眼的半径为1024/2PI=163
file_n = 'sample_streetview.png'
_img = cv2.imread(file_n)

height,width = _img.shape[:2]
cx = width/(2*math.pi)
cy = width/(2*math.pi)
img_hemi = np.zeros((int(cx+1)*2,int(cx+1)*2,3),dtype=np.uint8)

#理解四个象限
for col in range(img_hemi.shape[0]):  # col是x方向
    for row in range(img_hemi.shape[1]):  # row是y方向
        if row < cy:  # 界定第一、二象限
            if col < cx:  # 第二象限
                theta = np.pi - atan((row - cy) / (col - cx))
            else:  # 第一象限
                theta = np.abs(atan((row - cy) / (col - cx)))
        else:
            if col < cx:  # 第三象限
                theta = np.pi + np.abs(atan((row - cy) / (col - cx)))
            else:  # 第四象限
                theta = 2 * np.pi - atan((row - cy) / (col - cx))

        r = np.sqrt((col - cx) ** 2 + (row - cy) ** 2)

        x = (theta * width) / (2 * pi)
        y = (r * height) / cy

        img_hemi[row][col] = cv2.getRectSubPix(_img, (1, 1), (x, y))

# 外围设置为黑色
mask = np.zeros_like(img_hemi)
cv2.waitKey(0)
cv2.destroyAllWindows()
mask = cv2.circle(mask, (int(cx + 1), int(cx + 1)), int(cx + 1), (255, 255, 255), -1)
result = cv2.bitwise_and(img_hemi, mask)  # 使用“与”操作函数cv2.bitwise_and()对图像掩膜（遮挡）
cv2.waitKey(0)
cv2.destroyAllWindows()
out_name = 'fisheye_{}'.format(file_n)
cv2.imwrite(out_name, result)