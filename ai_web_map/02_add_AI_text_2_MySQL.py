# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""
import os
import pymysql
from pymysql import Error

def append_txt_to_mysql_by_id(mysql_config, table_name, id_column='id', 
                             text_column='ai_text', txt_base_path='./text_files/'):
    """
    基于ID列数据读取本地TXT文件内容并追加到MySQL的文本列中
    
    参数:
        mysql_config (dict): MySQL连接配置字典，包含:
                            host, user, password, database
        table_name (str): MySQL表名
        id_column (str): ID列名，默认为'id'
        text_column (str): 要更新的文本列名，默认为'ai_text'
        txt_base_path (str): 本地TXT文件的基础路径，默认为'./text_files/'
    
    返回:
        tuple: (成功更新的记录数, 失败记录数)
    
    说明:
        1. 连接到MySQL服务器
        2. 读取指定表的所有ID值
        3. 对于每个ID:
           a. 构建本地TXT文件路径: {txt_base_path}{id}.txt
           b. 如果文件存在，读取内容
           c. 更新MySQL中对应行的文本列
        4. 处理过程中记录成功和失败次数
    """
    
    success_count = 0
    fail_count = 0
    
    try:
        # 1. 连接到MySQL服务器
        connection = pymysql.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("成功连接到MySQL服务器")
        
        with connection.cursor() as cursor:
            # 2. 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                raise ValueError(f"表 '{table_name}' 不存在")
            
            # 3. 检查ID列是否存在
            cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{id_column}'")
            if not cursor.fetchone():
                raise ValueError(f"ID列 '{id_column}' 在表 '{table_name}' 中不存在")
            
            # 4. 检查文本列是否存在，不存在则添加
            cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{text_column}'")
            if not cursor.fetchone():
                print(f"文本列 '{text_column}' 不存在，将创建该列")
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {text_column} TEXT")
                connection.commit()
                print(f"已添加文本列 '{text_column}'")
            
            # 5. 获取所有ID值
            cursor.execute(f"SELECT {id_column} FROM {table_name}")
            ids = [row[id_column] for row in cursor.fetchall()]
            
            if not ids:
                print("表中没有数据")
                return (0, 0)
            
            print(f"找到 {len(ids)} 条记录需要处理")
            
            # 6. 处理每个ID
            for id_value in ids:
                try:
                    # 构建TXT文件路径
                    txt_file_path = os.path.join(txt_base_path, f"{id_value}.txt")
                    
                    # 检查文件是否存在
                    if not os.path.exists(txt_file_path):
                        print(f"文件不存在: {txt_file_path}")
                        fail_count += 1
                        continue
                    
                    # 读取文件内容
                    with open(txt_file_path, 'r', encoding='utf-8') as file:
                        text_content = file.read()
                    
                    # 更新MySQL中的记录
                    update_sql = f"""
                        UPDATE {table_name}
                        SET {text_column} = %s
                        WHERE {id_column} = %s
                    """
                    cursor.execute(update_sql, (text_content, id_value))
                    connection.commit()
                    
                    success_count += 1
                    if success_count % 100 == 0:
                        print(f"已处理 {success_count} 条记录")
                
                except Exception as e:
                    print(f"处理ID {id_value} 时出错: {str(e)}")
                    fail_count += 1
                    connection.rollback()
        
        print(f"处理完成: 成功 {success_count} 条, 失败 {fail_count} 条")
        return (success_count, fail_count)
    
    except Error as e:
        print(f"MySQL错误: {str(e)}")
        return (success_count, fail_count)
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return (success_count, fail_count)
    
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            print("MySQL连接已关闭")

# if __name__ == "__main__":
    # MySQL连接配置
    # mysql_config = {
    #     'host': 'localhost',
    #     'user': 'your_username',
    #     'password': 'your_password',
    #     'database': 'your_database'
    # }
    
    # 调用方法
    # success, fail = append_txt_to_mysql_by_id(
    #     mysql_config=mysql_config,
    #     table_name='your_table',
    #     id_column='id',  # 默认就是'id'，可省略
    #     text_column='ai_text',  # 默认就是'ai_text'，可省略
    #     txt_base_path='./text_files/'  # 默认路径，可省略
    # )
    
    # print(f"结果: 成功更新 {success} 条, 失败 {fail} 条")


if __name__ == "__main__":
    print('-')

