#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import base64
import yaml
import json
from urllib.parse import urlparse, unquote
import sys

def decode_base64(data):
    """解码base64数据"""
    try:
        # 添加padding如果必要
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('utf-8')
    except Exception as e:
        print(f"Base64解码失败: {e}")
        return None

def parse_subscription(url):
    """解析订阅链接"""
    try:
        headers = {
            'User-Agent': 'Clash/1.0'
        }
        
        print(f"正在下载订阅内容: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 尝试解码base64
        content = response.text.strip()
        decoded_content = decode_base64(content)
        
        if decoded_content:
            return decoded_content
        else:
            # 如果不是base64，直接返回内容
            return content
            
    except Exception as e:
        print(f"订阅解析失败: {e}")
        return None

def ss_to_clash(ss_url, name):
    """将SS链接转换为Clash格式"""
    try:
        # 移除 ss:// 前缀
        if ss_url.startswith('ss://'):
            ss_url = ss_url[5:]
        
        # 处理可能存在的@符号
        if '@' in ss_url:
            # 格式: method:password@server:port
            auth_part, server_part = ss_url.split('@', 1)
            server, port = server_part.split(':', 1)
        else:
            # 格式: base64(method:password)@server:port
            # 先解码base64部分
            encoded_part, server_part = ss_url.split('@', 1)
            auth_part = decode_base64(encoded_part)
            server, port = server_part.split(':', 1)
        
        if ':' in auth_part:
            method, password = auth_part.split(':', 1)
        else:
            # 如果auth_part已经是解码后的，可能包含#备注
            if '#' in auth_part:
                auth_part = auth_part.split('#')[0]
            method, password = auth_part.split(':', 1)
        
        # 处理可能的URL编码
        password = unquote(password)
        
        return {
            'name': name,
            'type': 'ss',
            'server': server,
            'port': int(port),
            'cipher': method,
            'password': password
        }
        
    except Exception as e:
        print(f"SS链接解析失败 {ss_url}: {e}")
        return None

def create_clash_config(proxies):
    """创建Clash配置文件"""
    config = {
        'port': 7890,
        'socks-port': 7891,
        'redir-port': 7892,
        'allow-lan': True,
        'mode': 'Rule',
        'log-level': 'info',
        'external-controller': '0.0.0.0:9090',
        'proxies': proxies,
        'proxy-groups': [
            {
                'name': '🚀 Auto',
                'type': 'url-test',
                'proxies': [proxy['name'] for proxy in proxies],
                'url': 'http://www.gstatic.com/generate_204',
                'interval': 300
            },
            {
                'name': '🌍 Global',
                'type': 'select',
                'proxies': ['🚀 Auto'] + [proxy['name'] for proxy in proxies]
            },
            {
                'name': '📱 Domestic',
                'type': 'select',
                'proxies': ['DIRECT', '🚀 Auto']
            }
        ],
        'rules': [
            'DOMAIN-SUFFIX,google.com,🌍 Global',
            'DOMAIN-SUFFIX,youtube.com,🌍 Global',
            'DOMAIN-SUFFIX,gstatic.com,🌍 Global',
            'DOMAIN-SUFFIX,facebook.com,🌍 Global',
            'DOMAIN-SUFFIX,twitter.com,🌍 Global',
            'DOMAIN-SUFFIX,instagram.com,🌍 Global',
            'DOMAIN-SUFFIX,github.com,🌍 Global',
            'DOMAIN-SUFFIX,githubusercontent.com,🌍 Global',
            'DOMAIN-KEYWORD,google,🌍 Global',
            'DOMAIN-KEYWORD,blogspot,🌍 Global',
            'DOMAIN-SUFFIX,cn,DIRECT',
            'DOMAIN-KEYWORD,china,DIRECT',
            'IP-CIDR,127.0.0.0/8,DIRECT',
            'IP-CIDR,192.168.0.0/16,DIRECT',
            'IP-CIDR,10.0.0.0/8,DIRECT',
            'IP-CIDR,172.16.0.0/12,DIRECT',
            'GEOIP,CN,DIRECT',
            'MATCH,🌍 Global'
        ]
    }
    return config

def main():
    # if len(sys.argv) < 2:
    #     print("使用方法: python3 subscribe_to_clash.py <订阅链接> [输出文件]")
    #     print("示例: python3 subscribe_to_clash.py https://your-subscribe-url.com ~/.config/clash/config.yaml")
    #     sys.exit(1)
    
    subscribe_url = r'https://no10-svip.urlapi-dodo.cyou/s?t=202f0fc6ee8960c4148ef10fd10a0907'
    output_file = './config.yaml'
    
    # 解析订阅
    content = parse_subscription(subscribe_url)
    if not content:
        print("无法获取订阅内容")
        sys.exit(1)
    
    print("订阅内容获取成功，开始解析节点...")
    
    # 分割行并解析节点
    lines = content.split('\n')
    proxies = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 解析节点名称（如果有#注释）
        name = f"Node-{i+1}"
        if '#' in line:
            url_part, name_part = line.split('#', 1)
            name = name_part.strip()
            line = url_part.strip()
        
        # 根据协议类型解析
        if line.startswith('ss://'):
            proxy = ss_to_clash(line, name)
            if proxy:
                proxies.append(proxy)
                print(f"✓ 解析成功: {name}")
        else:
            print(f"⚠ 跳过不支持的协议: {line[:50]}...")
    
    if not proxies:
        print("没有找到可用的节点")
        sys.exit(1)
    
    # 创建Clash配置
    clash_config = create_clash_config(proxies)
    
    # 保存配置文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Clash配置文件已生成: {output_file}")
    print(f"📊 共解析 {len(proxies)} 个节点")
    print("🎯 使用方法: clash -f {}".format(output_file))

if __name__ == "__main__":
    main()