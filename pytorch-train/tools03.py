from PIL import Image
import requests
from transformers import ChineseCLIPProcessor, ChineseCLIPModel
import time 
from functools import wraps
import torch

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
        
model = ChineseCLIPModel.from_pretrained(r"D:\BaiduNetdiskDownload\FiMaoTech\ImageSearcher\image_searcher\embedders\Chinese-CLIP\chinese-clip-vit-base-patch16").to(device)
processor = ChineseCLIPProcessor.from_pretrained(r"D:\BaiduNetdiskDownload\FiMaoTech\ImageSearcher\image_searcher\embedders\Chinese-CLIP\chinese-clip-vit-base-patch16")

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

if __name__ == "__main__":
    main()
