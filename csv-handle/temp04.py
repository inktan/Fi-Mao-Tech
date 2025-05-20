import csv

# 输入和输出文件路径
input_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_04-_.csv'

output_file = r'y:\GOA-AIGC\02-Model\安装包\stru\ade_20k_语义分割比例数据_05-_.csv'

with open(input_file, mode='r', encoding='utf-8') as infile, \
     open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.DictReader(infile)
    
    # 确保输出文件有相同的字段，只是id列会被修改
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in reader:
        # 分割id列并保留最后一项
        if 'date' in row and row['date']:
            parts = row['date'].split('.')
            row['date'] = parts[0]  # 取最后一部分
        
        writer.writerow(row)

print(f"处理完成，结果已保存到 {output_file}")