import json

# 1. 打开并读取 JSON 文件
with open(r"e:\work\sv_xiufenganning\文本分析\wuhan(3)(3).json", "r", encoding="utf-8") as f:
    data = json.load(f)  # 假设 data 是一个列表

# 2. 提取所有 "no" 值
no_values = [item["no"] for item in data if "no" in item]

# 3. 使用 set() 获取唯一值
unique_nos = set(no_values)

# 4. 统计唯一值数量
num_unique_nos = len(unique_nos)

print("所有 'no' 值:", no_values)
print("唯一 'no' 值:", unique_nos)
print("唯一 'no' 值的数量:", num_unique_nos)