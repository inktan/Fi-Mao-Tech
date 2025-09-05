import subprocess
import os
import time

def batch_copy_folders():
    base_source = r'f:\GoogleDrive\我的云端硬盘\work_fimo\svi_taiwan'
    base_destination = r'e:\svi_panorama'
    
    # 生成所有文件夹名称
    folders = []
    # 暂时离线到1200000
    for i in range(810000, 4000000, 10000):
        folders.append(f"sv_pano_{i}_{i + 10000}")
    
    total_folders = len(folders)
    print(f"发现 {total_folders} 个需要复制的文件夹")
    
    # 确保目标基础目录存在
    os.makedirs(base_destination, exist_ok=True)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    start_time = time.time()
    
    for index, folder in enumerate(folders, 1):
        source_path = os.path.join(base_source, folder)
        dest_path = os.path.join(base_destination, folder)
        
        print(f"[{index}/{total_folders}] 处理: {source_path}")
        print(f"[{index}/{total_folders}] 处理: {dest_path}")
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"  跳过 - 源文件夹不存在")
            skip_count += 1
            continue
        # continue
        
        # 检查是否已经复制过
        if os.path.exists(dest_path):
            print(f"  跳过 - 目标文件夹已存在")
            skip_count += 1
            # continue
        
        # 使用robocopy复制
        try:
            result = subprocess.run([
                'robocopy', source_path, dest_path,
                '/E', '/MT:6', '/R:5', '/W:10',
                '/NJH', '/NJS', '/NP'
            ], capture_output=True, text=True, encoding='gbk', timeout=3600)  # 1小时超时
            
            if result.returncode <= 1:
                print(f"  ✓ 复制成功")
                success_count += 1
            else:
                print(f"  ⚠ 复制警告 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"    错误: {result.stderr[:200]}...")  # 只显示前200字符
                success_count += 1  # robocopy警告通常仍算成功
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ 复制超时")
            error_count += 1
        except Exception as e:
            print(f"  ✗ 复制错误: {e}")
            error_count += 1
            
        # 统计信息
        elapsed_time = time.time() - start_time
        print(f"耗时: {elapsed_time:.2f} 秒")
    
    # 统计信息
    elapsed_time = time.time() - start_time
    print(f"\n{'='*50}")
    print("复制完成统计:")
    print(f"总文件夹数: {total_folders}")
    print(f"成功复制: {success_count}")
    print(f"跳过: {skip_count}")
    print(f"错误: {error_count}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个文件夹: {elapsed_time/total_folders:.2f} 秒")

# 运行批量复制
if __name__ == "__main__":
    batch_copy_folders()