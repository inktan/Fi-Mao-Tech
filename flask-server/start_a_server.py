import os,io,json,requests,time,base64,logging
from flask import Flask, Response,request, jsonify
from flask_cors import CORS
from gevent import pywsgi  
from PIL import Image
from functools import wraps
from io import BytesIO
from sv_bd import  get_lng_lat_info

def timer_decorator(func):
    """装饰器，用于计算函数运行的时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 运行耗时: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

class RunFlaskCommand:
    @timer_decorator
    def get_lng_lat_info(self):
        try:
            lng = request.args.get('lng')
            lat = request.args.get('lat')
            panoramas = get_lng_lat_info(lng,lat)
            return jsonify(panoramas=panoramas)
        except Exception as e:
            print(e)
            result = [str(e)]
            return jsonify(results=result)
    
    @timer_decorator
    def run(self, start=True):
        logging.info("Waiting for server to start ...")

        app = Flask(__name__, static_folder=None)
        CORS(app)

        app.add_url_rule("/get_lng_lat_info", "get_lng_lat_info", self.get_lng_lat_info, methods=["GET"])
        if start:
            server = pywsgi.WSGIServer(('0.0.0.0', 5002), app)
            print("Searcher Serving on port http://10.1.12.30:5002 ...")
            server.serve_forever()

def run(**kwargs):
    command = RunFlaskCommand(**kwargs)
    command.run()

if __name__ == "__main__":
    run()


