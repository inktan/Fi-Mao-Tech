import random
import string

import time
from functools import wraps

def timer_decorator(func):
    """装饰器，用于计算函数运行的时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 运行耗时: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

@timer_decorator
def generate_unique_random_numbers(n, length=10):
    characters = string.ascii_letters + string.digits
    unique_numbers = set()

    while len(unique_numbers) < n:
        random_str = ''.join(random.choices(characters, k=length))
        unique_numbers.add(random_str)

    return list(unique_numbers)

unique_random_numbers = generate_unique_random_numbers(100000000)
print(unique_random_numbers[:10])
