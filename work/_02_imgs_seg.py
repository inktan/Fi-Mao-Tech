# -*- coding: utf-8 -*-

import os, csv, torch, numpy, scipy.io, PIL.Image, torchvision.transforms,sys,time,gc
import pandas as pd
import numpy as np
from mit_semseg.models import ModelBuilder, SegmentationModule
from mit_semseg.utils import colorEncode
from PIL import Image
from tqdm import tqdm

start_time = time.time()
# 读取颜色文件
colors = scipy.io.loadmat('data/color150.mat')['colors']
# 获取分割后的图片
def visualize_result(pred):
    pred = pred.astype(numpy.uint8)
    pred_color = np.zeros((pred.shape[0], pred.shape[1], 3), dtype=np.uint8)
    for i in range(pred.shape[0]):  
        for j in range(pred.shape[1]):
            color_index = pred[i, j]

            # if color_index == 2:
            #     pred_color[i, j] = [255, 255, 255]
            # elif color_index == 4:
            #     pred_color[i, j] = [0, 255, 0]
            # elif color_index == 1:
            #     pred_color[i, j] = [0, 255, 0]
            # else:
            #     pred_color[i, j] = [0, 0, 0]

            pred_color[i, j] = colors[color_index]
                
    return pred_color

#  Network Builders
net_encoder = ModelBuilder.build_encoder(
    arch='resnet50dilated',
    fc_dim=2048,
    weights='ckpt/ade20k-resnet50dilated-ppm_deepsup/encoder_epoch_20.pth')
net_decoder = ModelBuilder.build_decoder(
    arch='ppm_deepsup',
    fc_dim=2048,
    num_class=150,
    weights='ckpt/ade20k-resnet50dilated-ppm_deepsup/decoder_epoch_20.pth',
    use_softmax=True)

crit = torch.nn.NLLLoss(ignore_index=-1)
segmentation_module = SegmentationModule(net_encoder, net_decoder, crit)
segmentation_module.eval()
# segmentation_module.cpu()
segmentation_module.cuda()

# Load and normalize one image as a singleton tensor batch
pil_to_tensor = torchvision.transforms.Compose([
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(
        mean=[0.485, 0.456, 0.406], # These are RGB mean+std values
        std=[0.229, 0.224, 0.225])])  # across a large photo dataset.

headers = ['id',]
pa_data = pd.read_csv('./data/object150_info.csv', encoding='utf8')
name_series = pa_data['Name']

for head in name_series:
    headers.append(head)

def seg_cal(image_folder,image_ss_csv):

    roots = []
    img_names = []
    img_paths = []

    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")

    for root, dirs, files in os.walk(image_folder):
        for file in files:
            if file.endswith(accepted_formats):
                roots.append(root)
                img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    with open('%s'%image_ss_csv ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(headers)

    for i, image_name in enumerate(tqdm(img_names)):

        image_name_path = img_paths[i]
        if not image_name.endswith('.jpg') and  image_name.endswith('.png') and  image_name.endswith('.jpeg'):
            continue
    
        try :            
            pil_image = Image.open(image_name_path).convert('RGB')

            # 获取图像的宽度和高度  
            width, height = pil_image.size
            # 计算总像素数量  
            total_pixels = width * height
            # 如果像素数量大于指定的最大值，进行缩放  
            max_pixels = 1000000 # 4g显存可以跑4000000
            if total_pixels > max_pixels:  
                # 计算缩放比例  
                scale = (max_pixels / total_pixels) ** 0.5  
                # 计算新的宽度和高度  
                new_width = int(width * scale)  
                new_height = int(height * scale)  
                # 创建一个新的缩放后的图像  
                pil_image = pil_image.resize((new_width, new_height))

            img_data = pil_to_tensor(pil_image)
            singleton_batch = {'img_data': img_data[None].cuda()}
            output_size = img_data.shape[1:]

            with torch.no_grad():
                scores = segmentation_module(singleton_batch, segSize=output_size)

            # Get the predicted scores for each pixel
            _, pred = torch.max(scores, dim=1)
            pred = pred.cpu()[0].numpy()

            # 获取整个分割后的结果
            vs_total = visualize_result(pred)
            # 保存分割后图像 rgb
            image = PIL.Image.fromarray(vs_total)
            tmp = image_name_path.replace('sv_','ss_rgb')
            folder_path = os.path.dirname(tmp)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            if ".jpg" in tmp:
                tmp = tmp.replace(".jpg",".png")
            elif ".jpeg" in tmp:
                tmp = tmp.replace(".jpeg",".png")
            image.save(tmp)

            # 新增mask代码
            tmp = image_name_path.replace('sv_','ss_mask')
            folder_path = os.path.dirname(tmp)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            if ".jpg" in tmp:
                tmp = tmp.replace(".jpg",".png")
            elif ".jpeg" in tmp:
                tmp = tmp.replace(".jpeg",".png")
            Image.blend(image, pil_image, 0.3).save(tmp)

            # 保存分割后图像 grey 灰度模式 用于裁剪瓦片计算
            # tmp = image_name_path.replace('directions','directions\sv_grey')
            # folder_path = os.path.dirname(tmp)
            # if not os.path.exists(folder_path):
            #     os.makedirs(folder_path)
            # image = PIL.Image.fromarray(pred.astype(numpy.uint8))
            # print(tmp)
            # if ".jpg" in tmp:
            #     tmp = tmp.replace(".jpg",".png")
            # elif ".jpeg" in tmp:
            #     tmp = tmp.replace(".jpeg",".png")
            # image.save(tmp)
            
            # 创建空的列表记录结果
            rate_list = ['%s'%image_name,]
            # 语义识别结果为150类
            all_num = pred.shape[0] * pred.shape[1]
            for n in range(150):
                # 计算分割后结果占比
                count = np.count_nonzero(pred == n)
                rate = count / all_num
                rate_list.append(rate)

            torch.cuda.empty_cache()
            # 确保图像文件被关闭
            if pil_image:
                pil_image.close()
            del pil_image
            gc.collect()

            # 将结果写入csv
            with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
                writer = csv.writer(f)
                writer.writerow(rate_list)
        except Exception as e :
            print(f'error:{e}')
        # finally :
        #     print('end')

    end_time = time.time()
    print('[-] 处理完成所有图片,耗时{:.2f}秒'.format(end_time - start_time))

if __name__ == "__main__":
    # 街景文件夹
    image_folder =r'E:\work\sv_amelie\sv_'
    # 语义分析结果输出文件夹
    image_ss_csv= os.path.join(r'E:\work\sv_amelie\sv_',"ss.csv")

    seg_cal(image_folder,image_ss_csv)







