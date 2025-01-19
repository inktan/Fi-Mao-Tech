from PIL import Image
from zhipuai import ZhipuAI
from io import BytesIO
import base64

client = ZhipuAI(api_key="985f74bb7af3b3576c22d7d09e0fd1bb.2w2LV9o69FCtqDce") # 请填写您自己的APIKey

img_path = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai-分析数据\ai_out\拉萨传统商业街景筛选-ai\181(180)-1.png'
with Image.open(img_path) as img:
    image_bytes = BytesIO()
    img.save(image_bytes, format=img.format)
    image_bytes = image_bytes.getvalue()

base64_image_data = base64.b64encode(image_bytes).decode('utf-8')

img_info={
    'img_path':img_path,
    'base64_image_data':base64_image_data,
}

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


response = client.chat.completions.create(
    # model="GLM-4V-Flash",
    # model="glm-zero-preview",
    # model="glm-4-Plus", 
    model="GLM-4V-Plus", 

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
    
print(response.choices[0].message.content)