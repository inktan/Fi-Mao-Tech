import requests as requests

# 在这里配置您在本站的API_KEY
api_key = "sk-FOIcGQMsc7236Ad6671CT3BLbkFJ03Dd2b5F428040b1B8e8"

headers = {
    "Authorization": 'Bearer ' + api_key,
}
question = input("输入您的问题\n")

params = {
    "messages": [
        {
            "role": 'user',
            "content": question
        }
    ],
    # 如果需要切换模型，在这里修改
    # "model": 'gpt-3.5-turbo'
    "model": 'gpt-4o'
}
response = requests.post(
    "https://aigptx.top/v1/chat/completions",
    headers=headers,
    json=params,
    stream=False
)
print(response.text)
res = response.json()
res_content = res['choices'][0]['message']['content']
print(res_content)