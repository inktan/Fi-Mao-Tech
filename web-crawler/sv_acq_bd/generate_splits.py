import os
import re
import math

def split_and_generate_scripts(source_path, output_dir, total_range, num_splits):
    """
    读取源脚本，修改其中的 index 判断逻辑，并生成多个分片脚本。
    """
    
    # 1. 检查源文件是否存在
    if not os.path.exists(source_path):
        print(f"错误: 找不到文件 {source_path}")
        return

    # 2. 读取源脚本内容
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. 定义要查找的正则表达式
    # 解释: 
    # (\s*) 捕获第一行的缩进
    # if index <= \d+: 匹配第一行判断
    # [\s\n]+ 匹配中间的换行和缩进
    # continue 匹配关键字
    # ... 匹配第二段判断
    pattern_str = r"(\s*)if index <= \d+:[\s\n]+continue[\s\n]+if index > \d+:[\s\n]+continue"
    
    match = re.search(pattern_str, content)
    
    if not match:
        print("错误: 在源脚本中未找到指定的 index 判断代码块，请检查格式。")
        return

    # 获取原始代码块的缩进 (indent)，用于保持生成代码的格式一致
    indent = match.group(1) 
    original_block = match.group(0)

    print(f"已找到目标代码块，正在准备切割... (总范围: 0-{total_range}, 分割数: {num_splits})")

    # 4. 创建输出文件夹
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"已创建输出目录: {output_dir}")

    # 5. 计算步长
    step = math.ceil(total_range / num_splits)

    # 6. 循环生成新文件
    for i in range(num_splits):
        # 计算当前分片的起止点
        start_idx = i * step
        end_idx = (i + 1) * step
        
        # 修正最后一个分片的结束点（虽然数学上刚好，但防止溢出通常是个好习惯）
        if i == num_splits - 1:
            end_idx = total_range + 1000 # 确保覆盖最后所有数据

        # 构建新的逻辑代码块
        # 逻辑：我们要保留 [start, end) 区间的数据
        # 所以：如果 index < start 则 continue (跳过前面)
        #       如果 index >= end 则 continue (跳过后面)
        new_logic = (
            f"{indent}if index < {start_idx}:\n"
            f"{indent}    continue\n"
            f"{indent}if index >= {end_idx}:\n"
            f"{indent}    continue"
        )

        # 替换文本
        new_content = content.replace(original_block, new_logic)

        # 定义新文件名
        new_filename = f"script_part_{i+1}.py"
        new_filepath = os.path.join(output_dir, new_filename)

        # 写入新文件
        with open(new_filepath, 'w', encoding='utf-8') as out_file:
            out_file.write(new_content)

        print(f"[{i+1}/{num_splits}] 生成: {new_filename} | 处理区间: {start_idx} <= index < {end_idx}")

    print("\n所有脚本生成完毕！")

# ================= 配置区域 =================
# 在这里修改你的源文件路径
source_script_path = r"web-crawler\sv_acq_bd\panorama_time_new.py"  # 你的原始脚本路径，例如 'train.py'
output_folder = r"E:\work\sv_wenhan_levon\20251211\output_scripts"       # 生成的新脚本存放的文件夹名称
# ===========================================

if __name__ == "__main__":
    # 如果你想测试，请确保当前目录下有一个名为 your_script.py 的文件
    # 或者修改上面的 source_script_path

    split_and_generate_scripts(source_script_path, output_folder, 4412, 36)
