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

response = client.embeddings.create(
    model="embedding-3", #填写需要调用的模型编码
     input=[
        "美食非常美味，服务员也很友好。",
        "这部电影既刺激又令人兴奋。",
        "阅读书籍是扩展知识的好方法。"
    ],
    dimensions=256, # 填写需要生成的向量维度
)
print(response)


# response = client.chat.completions.create(
#     # model="GLM-4V-Flash",  
#     model="glm-4-Plus",  
#     # model="glm-4v",  
#     # model="glm-zero-preview",
#     messages=[
#       {
#         "role": "user",
#         "content": [
#           {
#             "type": "text",
#             "text": "你是一个聪明且富有创造力的建筑设计师，请详细描述图的建筑特征"
#           },
#           {
#             "type": "image_url",
#             "image_url": {
#                 # "url" : "https://img1.baidu.com/it/u=1369931113,3388870256&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1703696400&t=f3028c7a1dca43a080aeb8239f09cc2f"
#                 "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
#             }
#           }
#         ]
#       }
#     ],
#     # stream=True,
#     )
# # for chunk in response:
# #     print(chunk.choices[0].delta.content)
    
# print(response.choices[0].message.content)