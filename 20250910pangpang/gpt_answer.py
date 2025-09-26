import pandas as pd
import os
import glob
import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

api_key = "sk-yK6p1Kzr3B285F7996D2T3BlBkFJ7064Acd099Ee48dfB9a6"

headers = {
    "Authorization": 'Bearer ' + api_key,
    # 'Content-Type': 'application/json'
}

# url = "https://api.ohmygpt.com"
# url = "https://apic.ohmygpt.com"
# url = "https://c-z0-api-01.hash070.com"

# url = "https://api.ohmygpt.com/v1"
# url = "https://apic.ohmygpt.com/v1"
# url = "https://c-z0-api-01.hash070.com/v1"

# url = "https://api.ohmygpt.com/v1/chat/completions"
# url = "https://apic.ohmygpt.com/v1/chat/completions"
url = "https://c-z0-api-01.hash070.com/v1/chat/completions"

# url = "https://aigptx.top/v1/chat/completions"

def chat_gpt4o(img_path,tree_names):
    
    query_text = f"This is the option for known tree names:{tree_names}. Please select a photo of this tree and its corresponding name from the given tree name options. If changing the tree name of the tree image is not in the given options, please correctly determine the tree name of this tree. Please only answer the words corresponding to the final tree name for me."
    
    with Image.open(img_path) as img:
        image_bytes = BytesIO()
        img.save(image_bytes, format=img.format)
        image_bytes = image_bytes.getvalue()

    base64_image_data = base64.b64encode(image_bytes).decode('utf-8')
    img_info={
        'img_path':img_path,
        'base64_image_data':base64_image_data,
    }

    params ={
    # "model": "doubao-vision-lite-32k-241015",
    # "model": "gpt-5-chat-latest",
    "model": "gpt-4o-mini",
    # "model": "gpt-4o-mini-audio-preview",
    # "model": "gpt-4o",
    # "model": "o3-mini",
    # "model": "o1-mini",
    #    "model": "gpt-3.5-turbo",
    #    "messages": [
    #       {
    #          "role": "user",
    #          "content": query_text
    #       }
    #    ],
    
    "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query_text},
                    {
                        "type": "image_url",
                        "image_url":{
                            "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
                            }
                    },
                ],
            }
        ],
        # "max_tokens":300,
        # "safe_mode": False
    }

    while True:
        try:
            response = requests.post(url,headers=headers,json=params,stream=False)
            # print(response)
            # print(response.text)

            res = response.json()
            # print(response)

            text = res['choices'][0]['message']['content']
            break
        except  Exception as e:
            print(e)
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)
            # text = ''
            return

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])
    return string_without_empty_lines

import pandas as pd
import os
import glob

def process_csv_with_incremental_save(csv_file_path, out_csv_file_path, target_tree_name):
    """
    读取CSV文件，遍历每一行，输出folder_path路径下的所有文件
    支持增量处理和实时保存，避免重复处理
    
    参数:
    csv_file_path: 输入的CSV文件路径
    out_csv_file_path: 输出的CSV文件路径
    target_tree_name: 目标树名称
    """
    
    # 读取CSV文件
    print("正在读取CSV文件...")
    try:
        df = pd.read_csv(csv_file_path)
        print(f"CSV文件读取成功，共 {len(df)} 行数据")
        print("列名:", df.columns.tolist())
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return
    
    # 检查必要的列是否存在
    required_columns = ['folder_path', 'unique_commonnames']
    for col in required_columns:
        if col not in df.columns:
            print(f"错误: 列 '{col}' 不存在于CSV文件中")
            print(f"可用的列: {df.columns.tolist()}")
            return
    
    # 初始化或读取已处理的结果文件
    processed_files = set()
    existing_results = []
    
    if os.path.exists(out_csv_file_path):
        try:
            existing_df = pd.read_csv(out_csv_file_path)
            existing_results = existing_df.to_dict('records')
            processed_files = set(existing_df['file_path'].tolist())
            print(f"找到已存在的输出文件，包含 {len(processed_files)} 个已处理文件")
        except Exception as e:
            print(f"读取已存在输出文件失败，将创建新文件: {e}")
    
    # 创建结果列表，初始化为已存在的结果
    results = existing_results.copy()
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(out_csv_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    # 计数器
    stats = {
        'total_processed': 0,
        'new_files': 0,
        'skipped_files': 0,
        'error_folders': 0
    }
    
    print("开始处理文件夹...")
    
    # 遍历每一行
    for index, row in df.iterrows():
        folder_path = row['folder_path']
        unique_commonnames = row['unique_commonnames']
        
        # 检查文件夹路径是否存在
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            print(f"警告: 路径不存在或不是文件夹 - {folder_path}")
            stats['error_folders'] += 1
            continue
        
        # 获取文件夹下的所有文件
        try:
            all_files = []
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    all_files.append(item_path)
            
            print(f"处理第 {index + 1} 行, 文件夹: {folder_path}, 找到 {len(all_files)} 个文件")
            
            # 处理每个文件
            for file_path in all_files:
                stats['total_processed'] += 1
                
                # 检查文件是否已经处理过
                if file_path in processed_files:
                    stats['skipped_files'] += 1
                    if stats['skipped_files'] % 100 == 0:  # 每100个跳过的文件打印一次
                        print(f"已跳过 {stats['skipped_files']} 个已处理文件...")
                    continue
                
                # gpt4o-mini 请求一次大约0.015元
                # 54,082 棵树木图片，大约需要54,082 *0.02=1081.64元

                # gpt-5-mini 请求一次大约0.03元
                # gpt-5-chat-latest 请求一次大约0.15元

                target_tree_name = chat_gpt4o(file_path,unique_commonnames)

                # 处理新文件
                new_result = {
                    'csv_row_index': index,
                    'folder_path': folder_path,
                    'file_path': file_path,
                    'filename': os.path.basename(file_path),
                    'unique_commonnames': unique_commonnames,
                    'target_tree_name': target_tree_name,
                }
                
                results.append(new_result)
                processed_files.add(file_path)
                stats['new_files'] += 1
                
                # 实时保存到CSV（每处理10个新文件保存一次，或者最后一批）
                if stats['new_files'] % 10 == 0 or stats['new_files'] == len(all_files):
                    try:
                        temp_df = pd.DataFrame(results)
                        temp_df.to_csv(out_csv_file_path, index=False, encoding='utf-8')
                        print(f"✓ 实时保存: 已处理 {stats['new_files']} 个新文件，总共 {len(results)} 条记录")
                    except Exception as e:
                        print(f"实时保存失败: {e}")
                
                # 显示进度
                if stats['new_files'] % 50 == 0:
                    print(f"进度: 新增 {stats['new_files']} 文件，跳过 {stats['skipped_files']} 文件")
                        
        except PermissionError:
            print(f"权限错误: 无法访问文件夹 {folder_path}")
            stats['error_folders'] += 1
        except Exception as e:
            print(f"错误: 无法读取文件夹 {folder_path} - {e}")
            stats['error_folders'] += 1
    
    # 最终保存
    try:
        result_df = pd.DataFrame(results)
        result_df.to_csv(out_csv_file_path, index=False, encoding='utf-8')
        print(f"\n最终保存完成！文件已保存到: {out_csv_file_path}")
    except Exception as e:
        print(f"最终保存失败: {e}")
        return None
    
    # 显示统计信息
    print(f"\n=== 处理统计 ===")
    print(f"总处理文件数: {stats['total_processed']}")
    print(f"新增文件数: {stats['new_files']}")
    print(f"跳过文件数(已处理): {stats['skipped_files']}")
    print(f"错误文件夹数: {stats['error_folders']}")
    print(f"最终结果记录数: {len(results)}")
    
    # 显示结果预览
    print("\n结果预览:")
    if len(results) > 0:
        preview_df = pd.DataFrame(results[:5])
        print(preview_df[['file_path', 'filename', 'target_tree_name']])
    else:
        print("没有找到任何文件")
    
    return pd.DataFrame(results)

# 使用示例
if __name__ == "__main__":
    # 指定文件路径
    input_csv_path = r"e:\work\sv_pangpang\out\sam_tree_nearest_name02.csv"
    output_csv_path = r"e:\work\sv_pangpang\out\sam_tree_target_name.csv"
    target_tree_name = "目标树种名称"  # 替换为实际的目标树名称
    
    # 检查输入文件是否存在
    if not os.path.exists(input_csv_path):
        print(f"错误: 输入CSV文件不存在 - {input_csv_path}")
    else:
        print("开始增量处理...")
        result = process_csv_with_incremental_save(
            input_csv_path, 
            output_csv_path, 
            target_tree_name
        )
