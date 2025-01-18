from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image
import requests
import os
import csv
from tqdm import tqdm
from PIL import Image, ImageDraw

# 检查是否有可用的GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# you can specify the revision tag if you don't want the timm dependency
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

def object_detection(img_paths):
    rate_lists= []
    for index, file_path in enumerate(tqdm(list(img_paths))):
        if index < 1559302:
            continue
        try:
            image = Image.open(file_path)
            inputs = processor(images=image, return_tensors="pt")
            outputs = model(**inputs)
            target_sizes = torch.tensor([image.size[::-1]])
            results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
            
            personCount = 0
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                # box = [round(i, 2) for i in box.tolist()]
                # print(
                        # f"Detected {model.config.id2label[label.item()]} with confidence "
                        # f"{round(score.item(), 3)} at location {box}"
                # )
                if label.item() ==1 :
                    personCount+=1
                        
                    # 将浮点坐标转换为整数坐标（Pillow 需要整数坐标）
                    point1_int = (box[0], box[1])
                    point2_int = (box[2], box[3])
                    draw = ImageDraw.Draw(image)
                    left_top = min(point1_int, point2_int)
                    right_bottom = max(point1_int, point2_int)
                    draw.rectangle([left_top, right_bottom], outline="red", width=3)
                    
                    # print(model.config.id2label[label.item()])
            # break
            # print(f" {file_path} at {personCount}")
            if personCount>0:
                
                tmp = file_path.replace('sv_pan_02','sv_pan_02_person').replace('D:','F:')
                folder_path = os.path.dirname(tmp)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                if ".jpg" in tmp:
                    tmp = tmp.replace(".jpg",".png")
                elif ".jpeg" in tmp:
                    tmp = tmp.replace(".jpeg",".png")
                # print(tmp)
                image.save(tmp)
            
            rate_list =[file_path,personCount] 
            rate_lists.append(rate_list)
            
            if index % 10000 == 0:
                with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(rate_lists)
                rate_lists = []
                
        except Exception as e:
            print(f"{e}")

    with open('%s' % image_ss_csv ,'a',encoding='utf-8' ,newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rate_lists)
        
def main():
    folder_path_list =[
        r'D:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02',# 01
        # r'D:\BaiduNetdiskDownload\sv_roadpoints_50m\sv_pan_02\454551_-0.226014548_51.51494206',# 02
        ]
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)

    print(len(img_paths))
    object_detection(img_paths)
    
if __name__ == '__main__':
    print('a01')
    image_ss_csv= os.path.join(r'F:\BaiduNetdiskDownload\sv_roadpoints_50m',"sv_pan_02_person_02.csv")
        
    with open('%s'%image_ss_csv ,'w' ,newline='') as f: 
        writer = csv.writer(f)
        writer.writerow(['path_name','person_count'])
    main()