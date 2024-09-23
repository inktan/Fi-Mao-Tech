
import pyautogui
import time
# import keyboard  # 用于模拟键盘快捷键
import csv
import pyperclip  # 用于访问剪贴板
import pandas as pd
from tqdm import tqdm

def move_click(x, y):
    pyautogui.moveTo(x-1920, y)
    pyautogui.click()
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)

    text = pyperclip.paste()
    return text

def simulate_open_web_address(address):
    # 输入网址
    url = f'https://shanghai.anjuke.com/community/?kw={address}'

    pyperclip.copy(url)
    pyautogui.moveTo(223-1920, 62)
    pyautogui.click()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(3.5)
    pyautogui.moveTo(317-1920, 690)
    pyautogui.click()
    time.sleep(2)
    # 点选数据-公交
    info_01 = move_click(910, 350)
    # 点选数据-地铁
    info_02 = move_click(710, 438)
    # 点选数据-学校
    info_03 = move_click(750, 438)
    # 点选数据-餐饮
    info_04= move_click(790, 438)
    # 点选数据-购物
    info_05 = move_click(830, 438)
    # 点选数据-医院
    info_06 = move_click(870, 438)
    # 点选数据-银行
    info_07 = move_click(910, 438)

    return [info_01,info_02,info_03,info_04,info_05,info_06,info_07]

if __name__ == '__main__':
    csv_path = r'baidu_api\id_address_lng_lat_01.csv'
    df = pd.read_csv(csv_path)
    csv_path = r'baidu_api\id_address_anjuke_01.csv'
        
    headers = ['id','address','address_01','lng','lat','公交','地铁','学校','餐饮','购物','医院','银行']
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)

    for i,row in enumerate(tqdm(df.iterrows())):
        print(i)

        id = row[1]['id']
        address = row[1]['address']
        lng = row[1]['lng']
        lat = row[1]['lat']

        if address.endswith("号"):
            address = address[:-1] + "弄"

        address_01 = address[:-1]
        if '街道' in address_01:
            address_01 = address_01.split('街道')[-1]
        elif '镇' in address_01:
            address_01 = address_01.split('镇')[-1]
        elif '工业区' in address_01:
            address_01 = address_01.split('工业区')[-1]
        elif '上海市' in address_01:
            address_01 = address_01.split('上海市')[-1]

        rate_list = [id,address,address_01,lng,lat]
        infos = simulate_open_web_address(address_01)
        rate_list.extend(infos)

        with open(csv_path,'a' ,newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            try:
                writer.writerow(rate_list)
            except Exception as e :
                rate_list = [e]
                writer.writerow(rate_list)


