import cv2
import numpy as np
import os

def colour_classification(folder_path,colour_classification_save_path):
    '''
    把图片中所有颜色A区域提取出来用黑色像素图表示
    颜色A区域外的其余部分用白色像素表示
    '''
    for filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, filename)
        
        image = cv2.imread(image_path)

        # 将图像转换为RGB颜色空间
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 定义目标颜色和相似度阈值
        target_color = np.array([70, 70, 70])
        similarity_threshold = 50

        # 计算每个像素与目标颜色的相似度
        distances = np.linalg.norm(image_rgb - target_color, axis=2)
        indices_black = np.where(distances <= similarity_threshold)
        indices_white = np.where(distances > similarity_threshold)

        image[indices_black] = [0, 0, 0]
        image[indices_white] = [255, 255, 255]

        cv2.imwrite(colour_classification_save_path+'/' + filename, image)

def Cropping(image_folder_path,colour_classification_save_path,output_folder):
    '''
    根据图片A的黑色区域
    将另一同样大小图片B的对应区域的其余部分用白色填充
    '''
    for filename in os.listdir(colour_classification_save_path):
        # 构建图像文件的完整路径
        reference_image_path = os.path.join(colour_classification_save_path, filename)
        fill_image_path = os.path.join(image_folder_path, filename)
            
        reference_image = cv2.imread(reference_image_path)

        # 将图像转换为RGB颜色空间
        image_rgb = cv2.cvtColor(reference_image, cv2.COLOR_BGR2RGB)

        # 定义目标颜色和相似度阈值
        target_color = np.array([0, 0, 0])
        similarity_threshold = 50

        # 计算每个像素与目标颜色的相似度
        distances = np.linalg.norm(image_rgb - target_color, axis=2)
        indices = np.where(distances <= similarity_threshold)

        image_to_crop  = cv2.imread(fill_image_path)

        white_background  = np.ones(image_to_crop .shape, dtype=np.uint8) * 255
        white_background[indices] = image_to_crop[indices]

        # 保存结果图片到指定文件夹
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, white_background )

image_folder_path = './1' # 街景文件夹
folder_path = './2' # 语义分析结果文件夹
colour_classification_save_path = './3' # 黑白分类结果文件夹
output_folder = './4' # 建筑区域裁剪图像保存后的文件夹

colour_classification(folder_path,colour_classification_save_path)
Cropping(image_folder_path,colour_classification_save_path,output_folder)

# ~~~
