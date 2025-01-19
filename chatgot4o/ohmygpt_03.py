import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

query_text="Please describe the urban environmental features of this street view image from the perspectives of walking, cycling, and driving."

# 在这里配置您在本站的API_KEY
api_key = "sk-FOIcGQMsc7236Ad6671CT3BLbkFJ03Dd2b5F428040b1B8e8"

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
    "model": "gpt-4o",
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
    # img_paths =[r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai-分析数据\ai_out\拉萨传统商业街景筛选-ai\181(180)-1.png']
    
    for i, img_path in enumerate(tqdm(img_paths)):
        # if i<=350:
            # continue
        # if i>108: 
        #     continue
        print(img_path)
        
        if '.jpg' in img_path:
            txt_path = img_path.replace('.jpg','.txt')
        elif '.png' in img_path:
            txt_path = img_path.replace('.png','.txt')
        elif '.JPG' in img_path:
            txt_path = img_path.replace('.JPG','.txt')
        elif '.jpeg' in img_pat:
            txt_path = img_path.replace('.jpeg','.txt')

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
    img_folder = r'F:\sv_suzhou\ai_descri'
    main(img_folder)