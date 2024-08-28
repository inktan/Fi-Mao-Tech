from PIL import Image
import requests
from transformers import ChineseCLIPProcessor, ChineseCLIPModel
import time 
from functools import wraps
import torch
import os
import pickle
from tqdm import tqdm
import sqlite3
import json
Image.MAX_IMAGE_PIXELS = None  # 这将移除像素数量的限制

def timer_decorator(func):
    """装饰器，用于计算函数运行的时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 运行耗时: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = r'start_a_server\image_searcher\embedders\Chinese-CLIP\chinese-clip-vit-base-patch16'
model = ChineseCLIPModel.from_pretrained(model_path).to(device)
processor = ChineseCLIPProcessor.from_pretrained(model_path)

db_path = r'd:\18-Goa\ai-clip\cn-clip-embedding.db'
table_name_data_normal = 'en_clip_data_normal'

@timer_decorator
def main():
    for i in range(10):
        
        # url = "https://clip-cn-beijing.oss-cn-beijing.aliyuncs.com/pokemon.jpeg"
        image = Image.open(r'c:\Users\wang.tan.GOA\Pictures\pokemon.jpeg')
        # Squirtle, Bulbasaur, Charmander, Pikachu in English
        texts = ["杰尼龟", "妙蛙种子", "小火龙", "皮卡丘"]

        # compute image feature
        inputs = processor(images=image, return_tensors="pt")
        image_features = model.get_image_features(**inputs.to(device)).to("cpu")
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)  # normalize
        # print(image_features)

        # compute text features
        # inputs = processor(text=texts, padding=True, return_tensors="pt")
        # text_features = model.get_text_features(**inputs)
        # text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)  # normalize

        # compute image-text similarity scores
        # inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
        # outputs = model(**inputs)
        # logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        # probs = logits_per_image.softmax(dim=1)  # probs: [[1.1419e-02, 1.0478e-02, 5.2018e-04, 9.7758e-01]]
        
def extact_feature():
    image_path_prefix = r"Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus_thumbnail_1k"
    # image_path_prefix = r"Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus_thumbnail_1k\thad"
    
    accepted_formats = (".png", ".jpg", ".jpeg")
    image_files = []
    for root, dirs, files in os.walk(image_path_prefix):
        image_files.extend(
            [os.path.join(root, file) for file in files if file.lower().endswith(accepted_formats)])
    
    # save_path = r'stored_embeddings_cn_clip.pickle'
    # embeddings = {}
        
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for idx, image_path in enumerate(tqdm(image_files)):
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt")
        image_features = model.get_image_features(**inputs.to(device)).to("cpu")
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)  # normalize

        dict_image_path = image_path.replace(image_path_prefix, "")
        # embeddings[dict_image_path] = {"image_embedding": image_features}
        
        json_string = json.dumps(image_features.detach().numpy()[0].tolist())
        
        # print(json_string)
        
        cursor.execute(f'''INSERT INTO {table_name_data_normal} (ID, PATH ,Embedding)
                         VALUES (?, ?, ?)''', (idx, dict_image_path, json_string))
        
        # if idx % 30000 == 0:
        #     with open(save_path, "wb") as file:
        #         pickle.dump(embeddings, file)
        # with open(save_path, "wb") as file:
        #     pickle.dump(embeddings, file)

    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # main()
    extact_feature()


