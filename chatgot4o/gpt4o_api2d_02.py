import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

query_text="讲个关于地球的笑话。"
# query_text="Please analyze how comfortable this street view image is for walking, cycling, or driving."
headers = {
# 'Authorization': 'Bearer fk192489-7dCTdBKwtYid3GzzAvy3om3gVEwSRBNU',
'Authorization': 'Bearer fk192612-pLVI3zuqAZCoCaeeDaZqmhia1uHmz4RE',
'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
'Content-Type': 'application/json'
}

url = "https://oa.api2d.net/v1/chat/completions"

def chat_gpt4o():

    payload = json.dumps({
    # "model": "o1-mini",
    # "model": "gpt-4o-mini",
    "model": "gpt-4o",
    # "model": "gpt-4-vision-preview",
    # "model": "gpt-4-turbo",
    # "model": "gpt-4-0613",
    # "model": "gpt-4-0314",

    # "model": "gpt-3.5-turbo-16k",
    # "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "user",
            "content": query_text
        }
    ],
    })

    while True:
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            converted_dict = json.loads(response.text)
            text = converted_dict['choices'][0]['message']['content']
            print(text)
            break
        except  Exception as e:
            print(e)
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)

def main():
    chat_gpt4o()

if __name__ == '__main__':
    main()
