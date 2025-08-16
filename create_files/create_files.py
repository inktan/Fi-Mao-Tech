import os

def modify_and_create_files(template_file, output_dir, total_range, interval):
    # 读取模板文件内容
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 计算需要生成的文件数量
    num_files = total_range // interval + (1 if total_range % interval else 0)
    
    # 生成每个文件
    for i in range(num_files):
        start = i * interval
        end = (i + 1) * interval if (i + 1) * interval < total_range else total_range
        
        # 替换模板中的数字为变量
        modified_content = template_content.replace(
            "if index <= 90000:",
            f"if index <= {start}:"
        ).replace(
            "if index > 100000:",
            f"if index > {end}:"
        ).replace(
            "output_ = r'f:\\work\\work_fimo\\svi_taiwan\\sv_pano_90000_100000'",
            f"output_ = r'f:\\work\\work_fimo\\svi_taiwan\\sv_pano_{start}_{end}'"
        )
        
        # 生成文件名
        filename = f"google_panorama_new_{start}_{end}.py"
        filepath = os.path.join(output_dir, filename)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"Created: {filename}")

# 使用示例
if __name__ == "__main__":
    template_file = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\web-crawler\sv_acq_google\google_panorama_new.py"  # 替换为你的模板文件路径
    output_directory = r"D:\Users\mslne\Documents\GitHub\Fi-Mao-Tech\web-crawler\sv_acq_google\output_scripts"      # 输出目录
    total_range = 84489                   # 总范围
    interval = 10000                        # 间隔
    
    modify_and_create_files(template_file, output_directory, total_range, interval)