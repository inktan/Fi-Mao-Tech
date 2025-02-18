import requests as requests
import json

from flask import Flask, Response,request, jsonify
from PIL import Image
import requests,base64
from flask_cors import CORS
from gevent import pywsgi  
from PIL import Image
from io import BytesIO
import logging
import time 
from flask import g

from zhipuai import ZhipuAI

import configparser

config_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file_path)
api_credentials = {
    'api_key': config.get('ohmygpt', 'api_key'),
    'expiration_date': config.get('ohmygpt', 'expiration_date')
}

def ohmygpt_stream(messages, is_stream):
    url = "https://aigptx.top/v1/chat/completions"
    api_key = "sk-FOIcGQMsc7236Ad6671CT3BLbkFJ03Dd2b5F428040b1B8e8"
    headers = {
        "Authorization":'Bearer ' + api_credentials['api_key'],
        "Content-Type": "application/json",
    }
    payload = {
        # "model": 'gpt-3.5-turbo',
        # "model": 'gpt-4o',
        "model": 'gpt-4o-mini',
        "messages": messages,
        "stream": is_stream,
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        if is_stream:
            for line in response.iter_lines():
                if line:
                    if line.decode('utf-8').split('data:', 1)[1].strip() == '[DONE]':
                        break

                    chunk = json.loads(line.decode('utf-8').split('data:', 1)[1].strip())
                    if 'choices' in chunk and chunk['choices']:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content')
                        if content is not None:
                            yield content
                            # print(content, end="")
                        else:
                            continue
        else:
            # print(response)
            res = response.json()
            # print(response)
            return res['choices'][0]['message']['content']

# question = input("输入您的问题\n")
# img_info={
#     # 'img_path':img_path,
#     'base64_image_data':base64_image_data,
# }
# messages=[{
#     "role": "user",
#     "content": [
#     {
#         "type": "text",
#         "text": "你是一个聪明且富有创造力的建筑设计师，请详细描述图的建筑特征"
#     },
#     {
#         "type": "image_url",
#         "image_url": {
#             "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
#         }
#     }
#     ]
# }]

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

@app.before_request
def start_timer():
    g.start = time.time()

@app.after_request
def log_request(response):
    if request.path.startswith('/ai_ohmygpt'):
        elapsed_time = time.time() - g.start
        logger.info(f'{request.remote_addr} - - [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] '
                    f'"{request.method} {request.path} {request.environ.get("SERVER_PROTOCOL")}" '
                    f'{response.status_code} {response.content_length} 请求耗时 {elapsed_time:.6f} s')
    return response

def run():
    print("Waiting for server to start ...")
    @app.route('/ai_ohmygpt',methods=['GET'])
    def ai_ohmygpt():
        question = request.args.get('question')
        try:
            print(f"User proinfo_img: { question}")
            messages=[{"role": "user", "content": question}]
        
            return Response(ohmygpt_stream(messages, True), mimetype='text/event-stream')
        except Exception as e:
            print(e)
            result = [str(e)]
            return jsonify(results=result)

    server = pywsgi.WSGIServer(('0.0.0.0', 6003), app)
    print("Searcher Serving on port 10.1.40.96:6003 ...")

    server.serve_forever()

if __name__ == "__main__":
    run()





