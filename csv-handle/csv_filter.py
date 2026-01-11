import pandas as pd
import os

csv_paths = [
    r'e:\work\sv_pangpang\sv_pano_20251219\points_info\CoS_GSV_30m_points_infos02.csv',
]

for csv_path in csv_paths:
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)

        # 检查type列是否存在
        # if 'type' not in df.columns:
        #     print(f"错误: 在文件 {csv_path} 中未找到 'type' 列")
        #     print(f"可用列: {list(df.columns)}")
        #     continue
        
        # 过滤数据：type列包含"住宅小区"
        # filtered_df = df[df['type'].str.contains('住宅小区', na=False)]
        # filtered_df = df[df['year'] == '住宅区']
        filtered_df = df[df['year'] != 0]
        
        print(f"文件: {os.path.basename(csv_path)}")
        print(f"总行数: {len(df)}")
        print(f"过滤后行数: {len(filtered_df)}")
        
        # 生成输出文件路径
        output_dir = os.path.dirname(csv_path)
        output_filename = os.path.basename(csv_path).replace('.csv', '_.csv')
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存为新的CSV文件
        filtered_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"已保存到: {output_path}")
        print("-" * 50)
        
    except Exception as e:
        print(f"处理文件 {csv_path} 时出错: {e}")



