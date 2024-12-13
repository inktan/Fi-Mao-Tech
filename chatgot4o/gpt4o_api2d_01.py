import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

# 39279 27506 = 11773
# 612 800 = 188 
# 11773/188=62.62
# 当前每个请求花费65个点

# 27506/382=72
# all 4541+2026 =6567
# start 10+800+382=1192
# end 6567-1192 = 5375*100=537500个点

# query_text="请分析这张街景图片对步行、骑行、车行的舒适度。"
query_text="Please analyze how comfortable this street view image is for walking, cycling, or driving."
headers = {
# 'Authorization': 'Bearer fk192489-7dCTdBKwtYid3GzzAvy3om3gVEwSRBNU',
'Authorization': 'Bearer fk192612-pLVI3zuqAZCoCaeeDaZqmhia1uHmz4RE',
'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
'Content-Type': 'application/json'
}

url = "https://oa.api2d.net/v1/chat/completions"

def chat_gpt4o(img_info):

    payload = json.dumps({
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
        "safe_mode": False
    })

    while True:
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            converted_dict = json.loads(response.text)
            text = converted_dict['choices'][0]['message']['content']
            break
        except  Exception as e:
            print(e)
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])
    with open(img_info['img_path'].replace('.jpg','.txt'), "w", encoding="utf-8") as file:
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

    for i, img_path in enumerate(tqdm(img_paths)):
        if i>30 and i<338:
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

        chat_gpt4o(img_info)

if __name__ == '__main__':
    img_folder = r'C:\Users\wang.tan.GOA\Desktop\_research\temp\sv_degree_960_720'
    main(img_folder)
