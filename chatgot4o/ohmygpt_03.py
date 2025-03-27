import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

query_text="Please describe the urban environmental features of this street view image from the perspectives of walking, cycling, and driving.Please have a conversation with me in English"
# query_text='''
# 作者根据声景的定义和研究目标，构建了一个包含15个指标的声景指标体系。这些指标分为四大类：
# 声音强度（Sound Intensity）：衡量声音的强弱，例如“嘈杂”或“安静”。
# 声景质量（Soundscape Quality）：衡量声音环境的整体质量，例如“感觉良好”或“感觉不好”。
# 声音来源（Sound Source）：包括交通噪声、人声、自然声音、机械噪声和音乐噪声。
# 感知情绪（Perceptual Emotion）：包括愉快、混乱、充满活力、平淡、平静、恼人、有事件感和单调等。
# 这些指标是基于人类对声音的主观感知设计的，而不是基于物理声学测量。

# 请对这张图片进行15个声景指标打分
# '''

# 在这里配置您在本站的API_KEY
api_key = "sk-yK6p1Kzr3B285F7996D2T3BlBkFJ7064Acd099Ee48dfB9a6"

headers = {
    "Authorization": 'Bearer ' + api_key,
    # 'Content-Type': 'application/json'
}

# url = "https://api.ohmygpt.com"
# url = "https://apic.ohmygpt.com"
# url = "https://c-z0-api-01.hash070.com"

# url = "https://api.ohmygpt.com/v1"
# url = "https://apic.ohmygpt.com/v1"
# url = "https://c-z0-api-01.hash070.com/v1"

# url = "https://api.ohmygpt.com/v1/chat/completions"
# url = "https://apic.ohmygpt.com/v1/chat/completions"
url = "https://c-z0-api-01.hash070.com/v1/chat/completions"

# url = "https://aigptx.top/v1/chat/completions"

def chat_gpt4o(img_info,txt_path):
    params ={
    "model": "doubao-vision-lite-32k-241015",
    # "model": "gpt-4o-mini",
    # "model": "gpt-4o-mini-audio-preview",
    # "model": "gpt-4o",
    # "model": "o3-mini",
    # "model": "o1-mini",
    #    "model": "gpt-3.5-turbo",
    #    "messages": [
    #       {
    #          "role": "user",
    #          "content": query_text
    #       }
    #    ],
    "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query_text},
                    # {"type": "text", "text": '图中有几辆车是什么车'},
                    {
                        "type": "image_url",
                        "image_url":{
                            "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
                            }
                    },
                ],
            }
        ],
        # "max_tokens":300,
        # "safe_mode": False
    }

    while True:
        try:
            response = requests.post(url,headers=headers,json=params,stream=False)
            # print(response)
            # print(response.text)

            res = response.json()
            # print(response)

            text = res['choices'][0]['message']['content']
            break
        except  Exception as e:
            print(e)
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)
            # text = ''
            return

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])

    folder_path = os.path.dirname(txt_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write(string_without_empty_lines)

def main(img_folder):
    roots = []
    img_names = []
    img_paths = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")
    for root, dirs, files in os.walk(img_folder):
        for file in files:
            if file.endswith(accepted_formats):
                roots.append(root)
                img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    # img_paths =[r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai\sv_degree_10_ai\work']
    # img_paths =[r'e:\work\sv_songguo\temp\sv\202210_180.jpg']
    
    for i, img_path in enumerate(tqdm(img_paths)):
        if i<=10:
            continue
        if i>1000: 
            continue
        # print(img_path)
        
        if '.jpg' in img_path:
            txt_path = img_path.replace('.jpg','.txt').replace('Suzhou-StreetView','Suzhou-SV-Ai')
        elif '.png' in img_path:
            txt_path = img_path.replace('.png','.txt').replace('Suzhou-StreetView','Suzhou-SV-Ai')
        elif '.JPG' in img_path:
            txt_path = img_path.replace('.JPG','.txt').replace('Suzhou-StreetView','Suzhou-SV-Ai')
        elif '.jpeg' in img_path:
            txt_path = img_path.replace('.jpeg','.txt').replace('Suzhou-StreetView','Suzhou-SV-Ai')

        if os.path.exists(txt_path):
            continue

        with Image.open(img_path) as img:
            image_bytes = BytesIO()
            img.save(image_bytes, format=img.format)
            image_bytes = image_bytes.getvalue()

        base64_image_data = base64.b64encode(image_bytes).decode('utf-8')
        img_info={
            'img_path':img_path,
            'base64_image_data':base64_image_data,
        }

        chat_gpt4o(img_info,txt_path)

if __name__ == '__main__':
    img_folder = r'F:\work\Suzhou-StreetView'
    main(img_folder)