from datetime import datetime

# 获取当前时间
now = datetime.now()
print(now)  # 输出：2024-06-10 14:30:45.123456（包含微秒）

# 格式化输出
formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
print(formatted_time)  # 输出：2024-06-10 14:30:45
