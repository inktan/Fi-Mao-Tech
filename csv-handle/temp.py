# 定义一个字符串
string_number = "2020"

try:
    # 将字符串转换为整数
    number = int(string_number)
    
    # 判断是否大于2019
    if number > 2019:
        print(f"{number} 大于 2019")
    else:
        print(f"{number} 不大于 2019")
except ValueError:
    # 如果字符串不能转换为整数，捕获异常并打印错误信息
    print(f"无法将字符串 '{string_number}' 转换为整数")

number = int('string_number')

# 判断是否大于2019
if number > 2019:
    print(f"{number} 大于 2019")
else:
    print(f"{number} 不大于 2019")
    