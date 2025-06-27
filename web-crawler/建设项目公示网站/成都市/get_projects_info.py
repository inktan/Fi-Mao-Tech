# -*- coding: utf-8 -*-
import requests
import sys
from pathlib import Path
import os
import requests
import csv
import time
from bs4 import BeautifulSoup
import os
import pickle
import json
from selenium.webdriver.chrome.service import Service

from datetime import datetime
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 获取当前文件的父目录的父目录（即上级目录）
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)  # 将上级目录加入 Python 路径

# 现在可以直接导入上级目录的模块
from file_utils import get_deepest_dirs, create_safe_dirname, PROJECT_KEYWORDS,PageCount
root_directory = r"Y:\\GOA-项目公示数据\\建设项目公示信息\\成都"  # 替换为你的目标文件夹路径
deepest_dir_names = get_deepest_dirs(root_directory)

def main():
    div_eles = r'''<div class="tdgl_cont"><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_76ff4b2971654eea8198cc54b139e5b8.shtml')">成都轨道交通集团有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_32db6e2d3a344aadb16f0ec371d8f51f.shtml')">成都市武侯卫生教育资产管理有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_c1f77caaa20944df938e8a803fb5895c.shtml')">成都市她妆美谷产业发展有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_bb25757e32f845eaa5b86361328a18f2.shtml')">成都武侯太平园城市更新建设有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_77fe74c6d2414be89513f63ec8af8cfa.shtml')">成都华显锦弘实业有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_1ce74a926a4e4f078bd1b735392bd4d0.shtml')">成都华显锦弘实业有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_2a544192a83c4bc7989cc95d4422fc83.shtml')">成都轨道交通集团有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/13/content_38980b2a293b44f3acd4f5a098ffb99a.shtml')">成都城建投资管理集团有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-13</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_17def0fd50f94c35a7d91e1b0124fec7.shtml')">成都兆和璟房地产开发有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_30ed941ed1294e86b14398e32f02c210.shtml')">成都城建投资管理集团有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_bfe9076035d04be9a686a630244fb138.shtml')">黄涛、陈骥</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_3313b854fdcf4f82b7ea30a6af0ab9c1.shtml')">成都轨道交通集团有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_79588c11859b4aa5837d15dd48830397.shtml')">成都轨道交通集团有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_99b2acab9cf34e77b9fd7d92b9a0dc0a.shtml')">成都市兴城建实业发展有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-06/06/content_0c35f2150276456d93e1fb1cb8772bdc.shtml')">成都市兴城建实业发展有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-06-06</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-05/30/content_53599e24c1594e0386d6a2cdb463b687.shtml')">蓉旅金沙（成都）置业有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-05-30</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-05/30/content_fdd18c112711462ea412ca9ac2bcf1e5.shtml')">成都武侯资本投资管理集团有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-05-30</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-05/30/content_d382d3b108d7410ea88aab8d79f87815.shtml')">成都市兴城建实业发展有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-05-30</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-05/30/content_cfb1d9d5c61f41e38b6f4bdd64520de2.shtml')">成都市兴城建实业发展有限责任公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-05-30</span>					          </div><div class="tdgl_c clear">					          <a href="javascript:;" onclick="aLinkClick('http://mpnr.chengdu.gov.cn/ghhzrzyj/jzxmgb/2025-05/30/content_4751eb4adf324f4690faa60fdf1afcb4.shtml')">成都市和天创科技股份有限公司</a>					          <span class="ggqx" style="color: rgb(218, 54, 16); font-size: 18px; width: 60px; float: left;">公布中</span>					          <span>2025-05-30</span>					          </div></div>'''
    # 解析HTML
    soup = BeautifulSoup(div_eles, 'html.parser')

    # 查找所有符合规则的div
    divs = soup.find_all('div', class_='tdgl_c clear')

    # 提取每个div中的链接、名称和日期
    results = []
    for div in divs:
        # 提取链接（从onclick属性中）
        a_tag = div.find('a', onclick=True)
        if a_tag and 'aLinkClick' in a_tag['onclick']:
            onclick_content = a_tag['onclick']
            # 提取URL（位于单引号之间）
            url_start = onclick_content.find("'") + 1
            url_end = onclick_content.find("'", url_start)
            url = onclick_content[url_start:url_end]
            
            # 提取名称（a标签的文本）
            name = a_tag.get_text(strip=True)
            
            # 提取日期（最后一个span标签的文本）
            spans = div.find_all('span')
            date = spans[-1].get_text(strip=True) if spans else "未知日期"
            
            # 提取状态（class="ggqx"的span文本）
            status_span = div.find('span', class_='ggqx')
            status = status_span.get_text(strip=True) if status_span else "未知状态"
            
            results.append({
                'name': name,
                'url': url,
                'date': date,
                'status': status
            })

    # 打印结果
    for item in results:
        print(f"名称: {item['name']}")
        print(f"链接: {item['url']}")
        print(f"日期: {item['date']}")
        print(f"状态: {item['status']}")
        print("-" * 50)

        # 提取标题
        project_name = item['name']
        # if any(keyword in project_name for keyword in PROJECT_KEYWORDS):
        #     continue

        # 提取链接
        pro_url = item['url']
        
        # 提取日期
        publish_date = item['date']
        
        project_name = project_name.strip()
        publish_date = publish_date.strip()
        try:
            year = int(publish_date[:4])  # 假设日期格式为"YYYY年MM月DD日"
        except (ValueError, IndexError):
            year = 0  # 日期格式不符合预期
        # 只添加新链接且年份>=2025的数据
        if int(year) < 2025:
            continue
        
        safe_dirname = create_safe_dirname(project_name, publish_date)
        # if safe_dirname in deepest_dir_names:
            # print(f"'{safe_dirname}' 已存在，跳过处理")
            # continue
        project_dir = os.path.join(base_output_dir, safe_dirname)
        path = Path(project_dir)
        # if path.exists() and path.is_dir():
            # print(f"文件夹 {project_dir} 已存在，跳过处理")
            # return True  # 或者 continue 如果在循环中
            # continue
        os.makedirs(project_dir, exist_ok=True)
        # 设置输出文件路径
        output_file = os.path.join(project_dir, "项目详情.txt")

        options = webdriver.ChromeOptions()  # 配置 chrome 启动属性
        # options.add_experimental_option("excludeSwitches", ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        # browser = webdriver.Chrome(options=options)
        chrome_driver_path = r'C:\Users\wang.tan.GOA\.wdm\drivers\chromedriver\win64\136.0.7103.113\chromedriver-win32\chromedriver.exe'
        service = Service(executable_path=chrome_driver_path)
        browser = webdriver.Chrome(service=service,options=options)

        browser.get(pro_url)
        wait = WebDriverWait(browser,3)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        html = browser.page_source

        return
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(pro_url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取基本信息
        content_div = soup.find(id="newcent")
        if not content_div:
            print("id='newcent'的标签")
            return False

        # 获取所有文本内容（去除多余空白）
        content = content_div.get_text(separator='\n', strip=True)
        # print(content)
        # 保存到txt文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"内容已保存到 {output_file}")

        

    return

# # 使用示例
# base_output_dir = f"Y:\\GOA-项目公示数据\\建设项目公示信息\\成都\\成都市\\未分类项目"

# if __name__ == "__main__":
#     main()
