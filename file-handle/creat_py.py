
# 打开文件并读取内容
file_path = r"D:\ProgramData\GitHub\Fi-Mao-Tech\web-crawler\SV_acq\panorama_to_sv\panorama_to_street_view.py"  # 替换为你的文件路径
with open(file_path, "r", encoding="utf-8") as f:
    template = f.read()

# 生成 20 个文件
for n in range(30):
    # 计算 start 和 end
    start = n * 720
    end = (n + 1) * 720

    # 替换模板中的 0 和 111
    file_content = template.replace("if i < 0:", f"if i < {start}:") \
                           .replace("if i >= 111:", f"if i >= {end}:")

    # 生成文件名
    file_name = "Y:\\GOA-AIGC\\02-Model\\安装包\\temp\py\\"+"panorama_to_street_view"+f"_{n+1:02d}.py"

    # 写入文件
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(file_content)

    print(f"已生成文件: {file_name}")
