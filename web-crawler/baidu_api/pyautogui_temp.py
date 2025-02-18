
import pyautogui
import time
import keyboard  # 用于模拟键盘快捷键
import csv
import pyperclip  # 用于访问剪贴板
import pandas as pd
from tqdm import tqdm

def move_click(x, y):
    pyautogui.moveTo(x-1920, y)
    time.sleep(0.3)
    pyautogui.click()
    time.sleep(0.3)

move_click(1845, 500)

# keyboard.press('f12')
# keyboard.release('f12')
pyautogui.hotkey('f12')
time.sleep(0.3)

move_click(1845, 500)

running = True
while running:
    keyboard.press('pagedown')
    keyboard.release('pagedown')
    time.sleep(0.3)

