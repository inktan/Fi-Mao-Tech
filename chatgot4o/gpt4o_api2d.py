import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

# 100点/0.35元
# 单纯的代码解答需要84点 0.294元 包含上下文
# 单纯的代码解答需要40点 0.14元 不包含上下文

# 本代码案例是图文一起
# 39279 27506 = 11773
# 612 800 = 188 
# 11773/188=62.62
# 当前每个请求花费65个点

# 27506/382=72
# all 4541+2026 =6567
# start 10+800+382=1192
# end 6567-1192 = 5375*100=537500个点

query_text="请从下面三个角度对这张街景图片进行研判分析打分：\
        1、街道元素干净程度打分，最高3分，最低0分，包含生态清洁（行道树绿化、沿街绿地垃圾、沿街花卉、隔离带绿化、口袋公园）、\
        路面清洁（路面垃圾、建筑垃圾、施工垃圾、道路破损、道路标识破损、斑马线破损、路缘石破损、人行道铺装破损、盲道破损）、\
        运输清洁（重型货车无遮盖、垃圾车辆无遮盖、非机动车运输无遮盖、扬尘污染）、夜间照明（道路照明、非机动车道照明、人行道照明、交叉口照明）、\
        污染治理（空气污染、噪声污染、光污染）;\
        2、街道整洁度打分，最高3分，最低0分，包含设施齐整（没有遮挡的消防栓、变电箱、空调外机低挂、信号灯遮挡、窨井盖缺失、架空钱）、\
        家具齐整（街道座椅、电话亭、交通隔离护栏、垃圾桶、公交站台、路灯、单独设置的人行道路灯、租车等候牌、公共卫生间、雕塑小品、邮筒、报刊事）、\
        停放齐整（自行车违章停放、电动车违章停放、机动车违章停放、路边摊贩）;\
        3、街道界面有序度打分，最高3分，最低0分，从职能有序（功能区分、商业工业交通居住）、\
        路权有序（机、非、人宽度比、机、非、人数量比、过街天桥、过街地道、公交专用道、盲道、无障碍设施非机等候区、公交等候区、骑行道铺装提示、人行道隔离设施）、\
        界面有序（广告牌、店招牌、街廓连续度、街道高宽比、开阔指数、建筑外立面和谐度街道整体视觉宜人度）；\
        请基于以上三个原则对街景图片进行打分，然后将三个角度的打分数据进行平均计算，给出一个最终打分结果，打分数据必须在0-3之间。请使用中文回答。"
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
            text = ''
            break

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])
    if '.jpg' in img_info['img_path']:
        with open(img_info['img_path'].replace('.jpg','.txt'), "w", encoding="utf-8") as file:
            file.write(string_without_empty_lines)
    elif '.png' in img_info['img_path']:
        with open(img_info['img_path'].replace('.png','.txt'), "w", encoding="utf-8") as file:
            file.write(string_without_empty_lines)
    elif '.JPG' in img_info['img_path']:
        with open(img_info['img_path'].replace('.JPG','.txt'), "w", encoding="utf-8") as file:
            file.write(string_without_empty_lines)
    elif '.jpeg' in img_info['img_path']:
        with open(img_info['img_path'].replace('.jpeg','.txt'), "w", encoding="utf-8") as file:
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
    img_paths =[r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai-分析数据\ai_out\拉萨传统商业街景筛选-ai\1374(-90)-3.png']
    # 单张图片消耗点数 计算前点数 23839
    # 单张图片消耗点数 计算后点数 23781 差 58点=0.203元

    # 1000P 人民币 ¥3.50

    for i, img_path in enumerate(tqdm(img_paths)):
        # if i>30 and i<338:
        #     continue

        with Image.open(img_path) as img:
            image_bytes = BytesIO()
            img.save(image_bytes, format=img.format)
            image_bytes = image_bytes.getvalue()

        base64_image_data = base64.b64encode(image_bytes).decode('utf-8')
        print(img_path)
        img_info={
            'img_path':img_path,
            'base64_image_data':base64_image_data,
        }

        chat_gpt4o(img_info)

if __name__ == '__main__':
    img_folder = r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai\sv_degree_10_ai\work'
    main(img_folder)
