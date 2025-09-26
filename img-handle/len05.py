import os
import csv
from datetime import datetime
from multiprocessing import Pool, cpu_count
import time

accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

def process_file(args):
    """处理单个文件的函数"""
    filename, root, image_ss_csv = args
    if filename.endswith(accepted_formats):
        rate_list = [filename]
        return rate_list
    return None

def write_to_csv_batch(writer, batch_data):
    """批量写入CSV"""
    for data in batch_data:
        if data:
            writer.writerow(data)

def main():
    # 获取当前日期和时间
    now = datetime.now()
    print("程序开始时间:", now.strftime("%Y-%m-%d %H:%M:%S"))
    
    folder_path = r'E:\stree_view'
    image_ss_csv = r'E:\sv_pan_names.csv'
    
    # 创建CSV文件并写入表头
    with open(image_ss_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index'])
    
    # 收集所有需要处理的文件路径
    file_args = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_args.append((filename, root, image_ss_csv))
    
    print(f"找到 {len(file_args)} 个文件需要处理")
    
    now = datetime.now()
    print("程序开始时间:", now.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 使用多进程处理
    num_processes = cpu_count()  # 使用所有可用的CPU核心
    print(f"使用 {num_processes} 个进程进行处理")
    
    batch_size = 1000  # 每处理1000个文件批量写入一次
    processed_count = 0
    start_time = time.time()
    
    with Pool(processes=num_processes) as pool:
        # 分批处理，避免内存占用过大
        for i in range(0, len(file_args), batch_size):
            batch_args = file_args[i:i + batch_size]
            
            # 使用imap_unordered提高效率
            results = []
            for result in pool.imap_unordered(process_file, batch_args):
                if result:
                    results.append(result)
                    processed_count += 1
            
            # 批量写入CSV
            if results:
                with open(image_ss_csv, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for result in results:
                        writer.writerow(result)
            
            # 显示进度
            if processed_count % 20000 == 0:
                current_time = datetime.now().strftime("%H:%M:%S")
                elapsed_time = time.time() - start_time
                files_per_second = processed_count / elapsed_time if elapsed_time > 0 else 0
                print(f"已处理: {processed_count} 个文件, 当前时间: {current_time}, "
                      f"处理速度: {files_per_second:.2f} 文件/秒")
    
    # 最终统计
    end_time = time.time()
    total_time = end_time - start_time
    print(f"处理完成! 总共处理 {processed_count} 个文件")
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均速度: {processed_count/total_time:.2f} 文件/秒")

if __name__ == "__main__":
    main()