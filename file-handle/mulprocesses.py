import subprocess
from concurrent.futures import ThreadPoolExecutor

def run_script(script):
    subprocess.run(['python', script], check=True)

scripts = [f"D:\\Users\\mslne\\Documents\\GitHub\\Fi-Mao-Tech\\chatgot4o\\zhipu05__{i}.py" for i in range(1, 191)]

print(scripts)

# 设置最大并发数为20
with ThreadPoolExecutor(max_workers=190) as executor:
    executor.map(run_script, scripts)
    