import pandas as pd
import os

def main():
    
    # 图片库所在文件夹
    folder_path_list =[
        r'F:\sv_suzhou\sv_pan'# 16
        # r'D:\Ai-clip-seacher\AiArchLibAdd-20240822\data-20240822',
        ]

    # 获取文件夹中的所有文件信息(含多级的子文件夹)
    img_paths = []
    img_names = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg", ".webp")

    for folder_path in folder_path_list:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(accepted_formats):
                    file_path = os.path.join(root, file)
                    img_paths.append(file_path)
                    img_names.append(file)

    id_list = [file.split('_')[0] for file in img_names]
    print(id_list)
    print(len(id_list))

    # 1. 读取 CSV 文件
    input_file = r'f:\sv_suzhou\points.csv'
    df = pd.read_csv(input_file)

    length_of_csv = len(df)
    print(length_of_csv)

    filtered_df = df[df['OBJECTID'].astype(str).isin(id_list)]
    
    length_of_csv = len(filtered_df)
    print(length_of_csv)

    # 保存过滤后的数据到新的CSV文件
    filtered_csv_file_path = r'f:\sv_suzhou\points_has_sv.csv'
    filtered_df.to_csv(filtered_csv_file_path, index=False)


if __name__ == '__main__':
    print('a01')
    main()




