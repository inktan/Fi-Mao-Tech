import os

def modify_and_create_files(template_file, output_dir, start_range, end_range, interval):
    # 读取模板文件内容
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 计算需要生成的文件数量
    total_range = end_range - start_range
    num_files = total_range // interval + (1 if total_range % interval else 0)
    
    # 生成每个文件
    for i in range(num_files):
        start = start_range + i * interval
        end = start_range + (i + 1) * interval
        if end > end_range:
            end = end_range
        
        # 替换模板中的变量
        modified_content = template_content.replace(
            "start = 844*10000",
            f"start = {start}"
        ).replace(
            "start01 = 844*10000",
            f"start01 = {start}"
        ).replace(
            "end = 846*10000",
            f"end = {end}"
        ).replace(
            "output_ = r'/root/autodl-tmp/20250815_sv_taiwan/svi_/sv_pano_8440000_8460000'",
            f"output_ = r'/root/autodl-tmp/20250815_sv_taiwan/svi_/sv_pano_{start}_{end}'"
        )
        
        # 生成文件名
        filename = f"gl_svi_{start}-{end}.py"
        filepath = os.path.join(output_dir, filename)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"Created: {filename}")

# 使用示例
if __name__ == "__main__":
    template_file = r"/root/autodl-tmp/code/gl_svi_844-846.py" # 替换为你的模板文件路径
    output_directory = r"/root/autodl-tmp/code/output_scripts" # 输出目录
    start = 970*10000                   # 总范围
    end = 1100*10000                   # 总范围
    interval = 10000                      # 间隔
    
    modify_and_create_files(template_file, output_directory, start, end, interval)