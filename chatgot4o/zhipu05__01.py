import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time
from PIL import Image
from zhipuai import ZhipuAI
from io import BytesIO
import base64

client = ZhipuAI(api_key="6e2dcd317fa92cd0afc45f5cc93d6ef3.wIWZcLg0M5bmCpL5")
query_text="Please describe the urban environmental features of this street view image from the perspectives of walking, cycling, and driving."

def chat_gpt4o(img_info,txt_path):
    try:
        response = client.chat.completions.create(
            model="GLM-4V-Flash",
            # model="glm-zero-preview",
            # model="glm-4-Plus", 
            # model="GLM-4V-Plus", 
            # model="GLM-4V-Plus-0111", 

            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": query_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        # "url" : "https://img1.baidu.com/it/u=1369931113,3388870256&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1703696400&t=f3028c7a1dca43a080aeb8239f09cc2f"
                        "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
                    }
                }
                ]
            }
            ],
            # stream=True,
            )
        # for chunk in response:
        #     print(chunk.choices[0].delta.content)
            
        text = response.choices[0].message.content
    except  Exception as e:
        print(e)
        # print("Connection error. Trying again in 2 seconds.")
        time.sleep(2)
        # text = ''
        return

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])
    # print(string_without_empty_lines)
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

    for i, img_path in enumerate(tqdm(img_paths)):
        if i < -10:
            continue
        if i >= 2520000000: 
            continue
  
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