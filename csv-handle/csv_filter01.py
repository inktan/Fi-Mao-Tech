def generate_alternating_list(A, length):
    # 初始化结果列表
    result = []
    
    # 生成列表
    for i in range(length):
        if i % 2 == 0:
            result.append(A + (i // 2))  # 添加 A + 0, A + 1, A + 2, ...
        else:
            result.append(A - (i // 2 + 1))  # 添加 A - 1, A - 2, A - 3, ...
    
    return result

# 示例
result = generate_alternating_list(2, 5)
print(result)  # 输出: [2, 3, 4, 5, 6, 7, 8
result = generate_alternating_list(7, 5)
print(result)  # 输出: [2, 3, 4, 5, 6, 7, 8
result = generate_alternating_list(12, 5)
print(result)  # 输出: [2, 3, 4, 5, 6, 7, 8
result = generate_alternating_list(17, 5)
print(result)  # 输出: [2, 3, 4, 5, 6, 7, 8]


