
import os
import glob
import re

def find_and_merge_split_files(directory):
    """
    在指定目录中查找所有符合条件的分割文件并合并
    
    Args:
        directory: 要搜索的目录路径
    """
    # 切换到指定目录
    original_dir = os.getcwd()
    os.chdir(directory)
    
    try:
        # 查找所有可能的文件前缀
        all_tar_files = glob.glob("*_*.tar")
        
        # 使用字典按前缀分组文件
        file_groups = {}
        for file in all_tar_files:
            # 使用正则表达式匹配 _数字.tar 模式
            match = re.search(r'(_\d+\.tar)$', file)
            if match:
                prefix = file[:match.start()]
                if prefix not in file_groups:
                    file_groups[prefix] = []
                file_groups[prefix].append(file)
        
        # 对每个前缀组进行处理
        for prefix, files in file_groups.items():
            # 确保文件按数字顺序排序
            files.sort(key=lambda x: int(re.search(r'_(\d+)\.tar$', x).group(1)))
            
            # 检查文件序列是否连续
            expected_numbers = set(range(1, len(files) + 1))
            actual_numbers = set(int(re.search(r'_(\d+)\.tar$', f).group(1)) for f in files)
            
            if expected_numbers != actual_numbers:
                print(f"警告: {prefix} 的文件序列不连续，跳过合并")
                continue
            
            # 确定输出文件名（去掉数字后缀）
            output_filename = f"{prefix}.tar"
            
            # 如果输出文件已存在，跳过
            if os.path.exists(output_filename):
                print(f"输出文件已存在，跳过: {output_filename}")
                continue
            
            print(f"合并 {len(files)} 个文件: {prefix}_*.tar -> {output_filename}")
            
            # 合并文件
            try:
                with open(output_filename, 'wb') as outfile:
                    for part_file in files:
                        with open(part_file, 'rb') as infile:
                            outfile.write(infile.read())
                        print(f"  已合并: {part_file}")
                
                # 验证合并后的文件大小
                total_size = sum(os.path.getsize(f) for f in files)
                if os.path.getsize(output_filename) == total_size:
                    print(f"合并完成: {output_filename} (大小验证成功)")
                    
                    # 删除原分割文件
                    for part_file in files:
                        os.remove(part_file)
                        print(f"  已删除: {part_file}")
                    
                    print(f"成功合并并删除了 {len(files)} 个文件\n")
                else:
                    print("错误: 合并后的文件大小与原始文件总和不匹配")
                    os.remove(output_filename)  # 删除不完整的合并文件
                    
            except Exception as e:
                print(f"合并过程中发生错误: {e}")
                if os.path.exists(output_filename):
                    os.remove(output_filename)  # 删除可能不完整的合并文件
        
        if not file_groups:
            print("未找到任何符合条件的分割文件")
            
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)

# 使用示例
if __name__ == "__main__":
    # 指定要处理的目录
    directory = r"E:\stree_view"
    find_and_merge_split_files(directory)