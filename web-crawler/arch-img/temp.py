from flask import Flask, Response,request, jsonify
from flask_cors import CORS
from gevent import pywsgi  
import logging
import time 
from flask import g
from zhipuai import ZhipuAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('run_flask_cmd_ai_chat_8803.log'),  # 日志文件名
        logging.StreamHandler()  # 控制台输出
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
# 对于所有路由
CORS(app, resources={r"/*": {"origins": "*"}})

@app.before_request
def start_timer():
    g.start = time.time()

@app.after_request
def log_request(response):
    if request.path.startswith('/ai_chat'):
        elapsed_time = time.time() - g.start
        logger.info(f'{request.remote_addr} - - [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] '
                    f'"{request.method} {request.path} {request.environ.get("SERVER_PROTOCOL")}" '
                    f'{response.status_code} {response.content_length} 请求耗时 {elapsed_time:.6f} s')
    return response


import configparser
config_file_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_file_path)
api_credentials = {
    'api_key': config.get('ZhipuAI_api_credentials', 'api_key'),
    'expiration_date': config.get('ZhipuAI_api_credentials', 'expiration_date')
}

client = ZhipuAI(api_key=api_credentials['api_key'])

def zhipuai_chat(messageList, is_stream=False):
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        # model="glm-4v",  # 填写需要调用的模型名称
        messages = messageList,
        stream = is_stream,
        )
    if is_stream:
        for chunk in response:
            # print(chunk.choices[0].delta.content)
            yield chunk.choices[0].delta.content
    else:
        answer = response.choices[0].message.content
        # print(answer)
        return answer
    
def run():
    print("Waiting for server to start ...")

    # 暂时web前端使用fetch进行ai对话
    @app.route('/ai_chat',methods=['POST'])
    def ai_chat():
        try:
            messageList = request.json
            return Response(zhipuai_chat(messageList['messages'], True), mimetype='text/event-stream')
        except Exception as e:
            print(e)
            result = [str(e)]
            return jsonify(results=result)

    server = pywsgi.WSGIServer(('0.0.0.0', 8803), app)
    print("Searcher Serving on port 39.98.218.136:8803 ...")

    server.serve_forever()

if __name__ == "__main__":
    run()





