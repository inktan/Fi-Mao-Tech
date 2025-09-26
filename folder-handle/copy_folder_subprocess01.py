import subprocess
import os
import time

def batch_copy_folders():
    base_source = r'f:\GoogleDrive\我的云端硬盘\temp\work_fimo\svi_taiwan'
    base_destination = r'E:\stree_view\root\autodl-tmp\20250815_sv_taiwan'
    
    # 生成所有文件夹名称
    folders = []
    # 暂时离线到1200000
    for i in range(3300000, 3660000, 10000):
        folders.append(f"sv_pano_{i}_{i + 10000}")
    
    total_folders = len(folders)
    print(f"发现 {total_folders} 个需要复制的文件夹")
    
    # 确保目标基础目录存在
    os.makedirs(base_destination, exist_ok=True)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    file_copied_count = 0  # 新增：统计实际复制的文件数量
    
    start_time = time.time()
    
    for index, folder in enumerate(folders, 1):
        source_path = os.path.join(base_source, folder)
        dest_path = os.path.join(base_destination, folder)
        
        print(f"\n[{index}/{total_folders}] 处理: {source_path}")
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"  跳过 - 源文件夹不存在")
            skip_count += 1
            continue
        # continue
        
        # 使用robocopy复制，仅复制目标中不存在的文件
        try:
            # 关键参数说明：
            # /E: 复制所有子目录，包括空目录
            # /MT:6: 使用6个线程
            # /R:5 /W:10: 重试5次，每次等待10秒
            # /XC /XN /XO: 排除已更改、较新、较旧的文件（只复制不存在的文件）
            # /NP: 不显示复制进度
            # /NFL /NDL: 不显示文件和目录列表（简化输出）
            result = subprocess.run([
                'robocopy', source_path, dest_path,
                '/E', '/MT:6', '/R:5', '/W:10',
                '/XC', '/XN', '/XO',  # 新增：仅复制目标中不存在的文件
                '/NJH', '/NJS', '/NP', '/NFL', '/NDL'
            ], capture_output=True, text=True, encoding='gbk', timeout=3600)  # 1小时超时
            
            # 解析输出获取复制的文件数
            # robocopy的返回信息在stdout中，格式类似："复制了xx个文件"
            copied_files = 0
            for line in result.stdout.splitlines():
                if "复制了" in line and "个文件" in line:
                    copied_files = int(line.split()[1])
                    break
            
            if copied_files > 0:
                print(f"  ✓ 复制成功，新增 {copied_files} 个文件")
                file_copied_count += copied_files
                success_count += 1
            elif result.returncode == 0:
                print(f"  跳过 - 所有文件已存在于目标文件夹")
                skip_count += 1
            elif result.returncode <= 1:
                print(f"  ✓ 复制完成，无新增文件")
                success_count += 1
            else:
                print(f"  ⚠ 复制警告 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"    错误: {result.stderr[:200]}...")  # 只显示前200字符
                success_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ 复制超时")
            error_count += 1
        except Exception as e:
            print(f"  ✗ 复制错误: {e}")
            error_count += 1
            
        # 实时统计信息
        elapsed_time = time.time() - start_time
        print(f"  已耗时: {elapsed_time:.2f} 秒 | 已复制 {file_copied_count} 个文件")
    
    # 最终统计信息
    elapsed_time = time.time() - start_time
    print(f"\n{'='*50}")
    print("复制完成统计:")
    print(f"总文件夹数: {total_folders}")
    print(f"成功处理: {success_count}")
    print(f"跳过: {skip_count}")
    print(f"错误: {error_count}")
    print(f"实际复制文件数: {file_copied_count}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个文件夹耗时: {elapsed_time/total_folders:.2f} 秒")

def batch_copy_folders02():
    base_source = r'f:\GoogleDrive\我的云端硬盘\temp\work_fimo\svi_taiwan'
    base_destination = r'E:\stree_view\root\autodl-tmp\20250815_sv_taiwan'
    
    # 生成所有文件夹名称
    folders = []
    # 暂时离线到1200000
    for i in range(3300000, 3660000,  20000):
        folders.append(f"sv_pano_{i}_{i + 20000}")
    
    total_folders = len(folders)
    print(f"发现 {total_folders} 个需要复制的文件夹")
    
    # 确保目标基础目录存在
    os.makedirs(base_destination, exist_ok=True)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    file_copied_count = 0  # 新增：统计实际复制的文件数量
    
    start_time = time.time()
    
    for index, folder in enumerate(folders, 1):
        source_path = os.path.join(base_source, folder)
        dest_path = os.path.join(base_destination, folder)
        
        print(f"\n[{index}/{total_folders}] 处理: {source_path}")
        
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            print(f"  跳过 - 源文件夹不存在")
            skip_count += 1
            continue
        # continue
        
        # 使用robocopy复制，仅复制目标中不存在的文件
        try:
            # 关键参数说明：
            # /E: 复制所有子目录，包括空目录
            # /MT:6: 使用6个线程
            # /R:5 /W:10: 重试5次，每次等待10秒
            # /XC /XN /XO: 排除已更改、较新、较旧的文件（只复制不存在的文件）
            # /NP: 不显示复制进度
            # /NFL /NDL: 不显示文件和目录列表（简化输出）
            result = subprocess.run([
                'robocopy', source_path, dest_path,
                '/E', '/MT:6', '/R:5', '/W:10',
                '/XC', '/XN', '/XO',  # 新增：仅复制目标中不存在的文件
                '/NJH', '/NJS', '/NP', '/NFL', '/NDL'
            ], capture_output=True, text=True, encoding='gbk', timeout=3600)  # 1小时超时
            
            # 解析输出获取复制的文件数
            # robocopy的返回信息在stdout中，格式类似："复制了xx个文件"
            copied_files = 0
            for line in result.stdout.splitlines():
                if "复制了" in line and "个文件" in line:
                    copied_files = int(line.split()[1])
                    break
            
            if copied_files > 0:
                print(f"  ✓ 复制成功，新增 {copied_files} 个文件")
                file_copied_count += copied_files
                success_count += 1
            elif result.returncode == 0:
                print(f"  跳过 - 所有文件已存在于目标文件夹")
                skip_count += 1
            elif result.returncode <= 1:
                print(f"  ✓ 复制完成，无新增文件")
                success_count += 1
            else:
                print(f"  ⚠ 复制警告 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"    错误: {result.stderr[:200]}...")  # 只显示前200字符
                success_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ 复制超时")
            error_count += 1
        except Exception as e:
            print(f"  ✗ 复制错误: {e}")
            error_count += 1
            
        # 实时统计信息
        elapsed_time = time.time() - start_time
        print(f"  已耗时: {elapsed_time:.2f} 秒 | 已复制 {file_copied_count} 个文件")
    
    # 最终统计信息
    elapsed_time = time.time() - start_time
    print(f"\n{'='*50}")
    print("复制完成统计:")
    print(f"总文件夹数: {total_folders}")
    print(f"成功处理: {success_count}")
    print(f"跳过: {skip_count}")
    print(f"错误: {error_count}")
    print(f"实际复制文件数: {file_copied_count}")
    print(f"总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每个文件夹耗时: {elapsed_time/total_folders:.2f} 秒")
# 运行批量复制
if __name__ == "__main__":
    # batch_copy_folders()
    batch_copy_folders02()
