# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

import configparser

def load_config(config_path='config.ini'):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_path)
    
    return {
        'amap': {
            'api_key': config.get('AMAP', 'api_key'),
            'base_url': config.get('AMAP', 'base_url'),
            'geocode_endpoint': config.get('AMAP', 'geocode_endpoint'),
            'driving_endpoint': config.get('AMAP', 'driving_endpoint')
        },
        'baidu': {
            'api_key': config.get('BAIDU_MAP', 'api_key'),
            'base_url': config.get('BAIDU_MAP', 'base_url'),
            'geocode_endpoint': config.get('BAIDU_MAP', 'geocode_endpoint')
        },
        'openai': {
            'api_key': config.get('OPENAI', 'api_key'),
            'base_url': config.get('OPENAI', 'base_url'),
            'chat_endpoint': config.get('OPENAI', 'chat_endpoint')
        },
        'mysql': {
            'host': config.get('MYSQL', 'host'),
            'port': config.getint('MYSQL', 'port'),
            'user': config.get('MYSQL', 'user'),
            'password': config.get('MYSQL', 'password'),
            'database': config.get('MYSQL', 'database')
        }
    }

# if __name__ == '__main__':
#     config = load_config()
#     print(config['amap']['api_key'])

if __name__ == "__main__":
    print('-')