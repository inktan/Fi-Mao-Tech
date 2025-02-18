import requests as requests
import json

def create_openai_chat_completion_stream(model, messages):
    url = "https://aigptx.top/v1/chat/completions"
    api_key = "sk-FOIcGQMsc7236Ad6671CT3BLbkFJ03Dd2b5F428040b1B8e8"
    headers = {
        "Authorization":'Bearer ' + api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                if line.decode('utf-8').split('data:', 1)[1].strip() == '[DONE]':
                    break

                chunk = json.loads(line.decode('utf-8').split('data:', 1)[1].strip())
                if 'choices' in chunk and chunk['choices']:
                    delta = chunk['choices'][0].get('delta', {})
                    content = delta.get('content')
                    if content is not None:
                        print(content, end="")
                    else:
                        continue

question = input("输入您的问题\n")

create_openai_chat_completion_stream(
    # model="gpt-4o-mini",
    model="gpt-4o",
    # model="gpt-4o-mini",
    messages=[{"role": "user", "content": question}]
)

