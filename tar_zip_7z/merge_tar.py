def merge_split_files(output_filename, input_prefix):
    part_files = []
    i = 1
    
    # 找出所有部分文件
    while True:
        filename = f"{input_prefix}_0{i}.tar"  # split默认使用3位数字后缀
        try:
            with open(filename, 'rb') as f:
                part_files.append(filename)
            i += 1
        except FileNotFoundError:
            break
    
    if not part_files:
        print("未找到分割文件")
        return
    
    # 按数字顺序排序文件
    part_files.sort()
    
    # 合并文件
    with open(output_filename, 'wb') as outfile:
        for part_file in part_files:
            with open(part_file, 'rb') as infile:
                outfile.write(infile.read())
            print(f"已合并: {part_file}")
    
    print(f"合并完成: {output_filename}")

# 使用示例
merge_split_files(r"g:\stree_view\tar_0444\sv_pano_11110000_11120000.tar", r"g:\stree_view\tar_0444\sv_pano_11110000_11120000")