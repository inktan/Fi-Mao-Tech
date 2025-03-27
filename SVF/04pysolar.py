from pysolar.solar import get_altitude, get_azimuth
from datetime import datetime, timedelta
import pytz
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

# 给定的经纬度
latitude = 52.776188701508325  # 纬度
longitude = -1.238319474       # 经度

# 设置时区（英国伦敦时区，UTC+0）
timezone = pytz.timezone('Europe/London')

# 定义日期（例如：2023年10月1日）
date = datetime(2023, 10, 1, tzinfo=timezone)

# 创建一个空的 DataFrame，用于存储结果
data = []

# 遍历一天中的每个小时和分钟
for hour in range(24):  # 0 到 23 小时
    for minute in range(0, 60, 6):  # 每 15 分钟计算一次
        # 构造当前时间
        current_time = date + timedelta(hours=hour, minutes=minute)
        
        # 计算太阳高度角和方位角
        altitude = get_altitude(latitude, longitude, current_time)
        azimuth = get_azimuth(latitude, longitude, current_time)
        
        # 将结果添加到列表中
        data.append([hour, minute, altitude, azimuth])

# 将列表转换为 DataFrame
df = pd.DataFrame(data, columns=['Hour', 'Minute', 'Altitude', 'Azimuth'])

# 输出 DataFrame
df = df[df['Altitude']>0]
df.reset_index(drop=True, inplace=True)

# 将Altitude和Azimuth列转换为弧度
df['Altitude_r'] = df['Altitude'].apply(math.radians)
df['Azimuth_r'] = df['Azimuth'].apply(math.radians)

# 打印结果
print(df)

# 创建极坐标图
plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection='polar')

# 绘制太阳轨迹
ax.plot(df['Azimuth_r'], df['Altitude'], marker='o', linestyle='-', color='red', label='Sun Path')

ax.set_ylim(0, 90)  # 设置高度角的范围
ax.invert_yaxis()  # 反转方位角轴
ax.set_yticks([0,30,60])
ax.set_theta_direction(-1)  # 将角度增加方向设置为逆时针
ax.set_theta_zero_location('N')  # 将0度方位角指向北方

# 设置极坐标图的标题和标签
# ax.set_title("Sun's Trajectory in Polar Coordinates", va='bottom')

# 添加图例
plt.legend(loc='upper right')
for i,v in enumerate(['N','E','s','W']):
    ax.text(i*0.5*np.pi,-13,v,va='center',ha='center')

# 显示图形
plt.show()
# plt.savefig(r'E:\work\sv_j_ran\20241227')


