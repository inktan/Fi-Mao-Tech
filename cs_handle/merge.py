import os

def merge_cs_files(source_dir, output_file):
    """
    合并指定目录下所有.cs文件内容到单个文件，跳过注释行
    
    :param source_dir: 要搜索的根目录
    :param output_file: 输出的合并文件路径
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 添加文件头说明
        # outfile.write("// Merged C# files from: {}\n".format(source_dir))
        # outfile.write("// Total files merged: {}\n\n".format(
        #     sum(1 for _ in find_cs_files(source_dir))))
        
        for filepath in find_cs_files(source_dir):
            # 写入原文件名作为分隔标记
            # outfile.write("\n// ===== File: {} =====\n".format(filepath))
            
            with open(filepath, 'r', encoding='utf-8') as infile:
                for line in infile:
                    stripped = line.strip()
                    # 跳过空行和单行注释
                    if not stripped or stripped.startswith(('//', '///')):
                        continue
                    outfile.write(line)

def find_cs_files(directory):
    """
    递归查找目录下所有.cs文件
    
    :param directory: 要搜索的目录
    :return: 生成器，产生每个.cs文件的完整路径
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.cs'):
                yield os.path.join(root, file)

if __name__ == '__main__':
    # source_directory = input("请输入要搜索的目录路径: ")
    source_directory = r'D:\ProgramData\GitHub\RevitApi_\tools_2025\InfoStrucFormwork'
    output_path = os.path.join(source_directory, 'merged_output.cs')
    
    merge_cs_files(source_directory, output_path)
    print(f"合并完成！结果已保存到: {output_path}")