import os
from openai import OpenAI


# 在这里配置您在本站的API_KEY
API_KEY = "sk-FOIcGQMsc7236Ad6671CT3BLbkFJ03Dd2b5F428040b1B8e8"

# headers = {
#     "Authorization": 'Bearer ' + api_key,
    # 'Content-Type': 'application/json'
# }
BASE_URL = "https://c-z0-api-01.hash070.com/v1/chat/completions"

MODEL = "gpt-4o",

base_url, api_key, model = BASE_URL, API_KEY, MODEL
client = OpenAI(api_key=api_key, base_url=base_url)

def test(stream=True):
    query = f"please introduce yourself briefly, no more than ten words."
    messages = [{"role": "user", "content": query}]
    req_dic = {"model": model, "messages": messages, "stream": stream}
    response = client.chat.completions.create(**req_dic)
    if stream:
        res = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                res += chunk.choices[0].delta.content
        pass

test()