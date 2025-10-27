import datetime

# 时间戳（毫秒）
timestamp_ms = 1761203592000

# 转换为秒
timestamp_sec = timestamp_ms / 1000

# 转换为可读时间
readable_time = datetime.datetime.fromtimestamp(timestamp_sec)

print(f"原始时间戳: {timestamp_ms}")
print(f"转换后的时间: {readable_time}")
print(f"格式化时间: {readable_time.strftime('%Y-%m-%d %H:%M:%S')}")