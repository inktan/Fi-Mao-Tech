from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from tqdm import tqdm
import os
import sys

def main(folder_path,prompt):
    model_path = os.path.join(sys.path[0],'image-to-text','blip-image-captioning-large')
    processor = BlipProcessor.from_pretrained(model_path)
    model = BlipForConditionalGeneration.from_pretrained(model_path).to("cpu")
    filenames = os.listdir(folder_path)
    for i, filename in enumerate(tqdm(filenames)):
        if filename.endswith('.jpg') or  filename.endswith('.png') or  filename.endswith('.jpeg'):
            img_path = os.path.join(folder_path, filename)  # 文件路径
            raw_image = Image.open(img_path).convert('RGB')

            inputs = processor(raw_image, prompt,return_tensors="pt").to("cpu")
            out = model.generate(**inputs)
            out_describe = processor.decode(out[0], skip_special_tokens=True)
            
            # 将字典写入到txt文件  
            with open(folder_path +r"\\" + filename+'.txt', 'w') as f:  
                f.write(out_describe)

if __name__ == "__main__":
    folder_path = r"D:\BaiduSyncdisk\FiMaoTech\Optimization_SV_Classification\work\sv\06-kmeans\kmeans_100\0"

    # 可以指定其他对话提示词
    prompt='The building depicted in the figure is'

    main(folder_path,prompt)






