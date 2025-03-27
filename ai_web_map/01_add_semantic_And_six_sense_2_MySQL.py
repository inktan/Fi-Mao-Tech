# -*- coding: utf-8 -*-
"""

Created on  2024.9.30
@author: 非猫科技

"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler

def process_csv_and_write_to_mysql(csv_path, table_name, id_column='id', 
                                  mysql_conn=None, mysql_url=None):
    """
    处理CSV文件并将归一化后的数据写入MySQL数据库
    
    参数:
        csv_path (str): CSV文件路径
        table_name (str): MySQL表名
        id_column (str): ID列名，默认为'id'
        mysql_conn (dict): MySQL连接参数字典，包含host, user, password, database等
        mysql_url (str): 可选的SQLAlchemy连接URL，格式为:
                         'mysql+pymysql://user:password@host/database'
    
    返回:
        bool: 操作是否成功
    
    说明:
        1. 读取CSV文件到Pandas DataFrame
        2. 检查ID列是否存在
        3. 对除ID列外的所有列进行归一化(Min-Max归一化)
        4. 将处理后的数据写入MySQL
            - 如果表不存在则创建新表
            - 如果表存在则检查列是否存在
            - 基于ID列匹配追加新列数据
    """
    
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 2. 检查ID列是否存在
        if id_column not in df.columns:
            raise ValueError(f"ID列 '{id_column}' 在CSV文件中不存在")
        
        # 3. 对除ID列外的所有列进行归一化
        # 复制原始DataFrame用于归一化
        normalized_df = df.copy()
        # 获取需要归一化的列名(排除ID列)
        columns_to_normalize = [col for col in df.columns if col != id_column]
        
        if not columns_to_normalize:
            raise ValueError("没有找到需要归一化的列(除ID列外)")
        
        # 初始化归一化器
        scaler = MinMaxScaler()
        # 对选定的列进行归一化
        normalized_df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
        
        # 4. 连接到MySQL数据库
        if mysql_url is None:
            if mysql_conn is None:
                raise ValueError("必须提供mysql_conn或mysql_url参数")
            mysql_url = f"mysql+pymysql://{mysql_conn['user']}:{mysql_conn['password']}@{mysql_conn['host']}/{mysql_conn['database']}"
        
        engine = create_engine(mysql_url)
        
        # 5. 写入MySQL数据库
        with engine.connect() as conn:
            # 检查表是否存在
            table_exists = engine.dialect.has_table(conn, table_name)
            
            if not table_exists:
                # 表不存在，创建新表并写入所有数据
                normalized_df.to_sql(
                    name=table_name,
                    con=engine,
                    index=False,
                    if_exists='fail'
                )
                print(f"创建新表 {table_name} 并写入所有数据")
            else:
                # 表已存在，需要检查列并更新数据
                # 获取现有表的列信息
                existing_columns = pd.read_sql(f"SHOW COLUMNS FROM {table_name}", conn)['Field'].tolist()
                
                # 检查ID列是否存在于目标表中
                if id_column not in existing_columns:
                    raise ValueError(f"ID列 '{id_column}' 在目标表中不存在")
                
                # 准备要添加的新列
                new_columns = [col for col in columns_to_normalize if col not in existing_columns]
                
                if new_columns:
                    # 需要添加新列
                    for column in new_columns:
                        # 获取列的数据类型
                        dtype = str(normalized_df[column].dtype)
                        mysql_type = 'FLOAT'  # 归一化后的数据都是浮点数
                        
                        # 添加新列
                        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {mysql_type}")
                        print(f"添加新列: {column}")
                
                # 更新数据
                # 首先获取目标表中现有的ID
                existing_ids = pd.read_sql(f"SELECT {id_column} FROM {table_name}", conn)[id_column]
                
                # 筛选出存在于目标表中的ID对应的数据
                update_df = normalized_df[normalized_df[id_column].isin(existing_ids)]
                
                if not update_df.empty:
                    # 准备更新语句
                    for _, row in update_df.iterrows():
                        # 构建SET部分
                        set_values = []
                        for col in columns_to_normalize:
                            if col in existing_columns:  # 只更新已存在的列
                                set_values.append(f"{col} = {row[col]}")
                        
                        if set_values:  # 如果有需要更新的列
                            update_sql = f"""
                                UPDATE {table_name}
                                SET {', '.join(set_values)}
                                WHERE {id_column} = {row[id_column]}
                            """
                            conn.execute(update_sql)
                    
                    print(f"更新了 {len(update_df)} 行数据")
                
                # 插入新ID的数据(如果有)
                new_ids_df = normalized_df[~normalized_df[id_column].isin(existing_ids)]
                if not new_ids_df.empty:
                    new_ids_df.to_sql(
                        name=table_name,
                        con=engine,
                        index=False,
                        if_exists='append'
                    )
                    print(f"新增了 {len(new_ids_df)} 行数据")
        
        return True
    
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return False

# if __name__ == "__main__":
    # MySQL连接配置(方式1)
    # mysql_config = {
    #     'host': 'localhost',
    #     'user': 'your_username',
    #     'password': 'your_password',
    #     'database': 'your_database'
    # }
    
    # 或者使用SQLAlchemy连接URL(方式2)
    # mysql_url = 'mysql+pymysql://user:password@localhost/database'
    
    # 调用方法
    # success = process_csv_and_write_to_mysql(
    #     csv_path='your_file.csv',
    #     table_name='normalized_data',
    #     id_column='id',  # 默认就是'id'，可省略
    #     mysql_conn=mysql_config
        # 或者使用: mysql_url=mysql_url
    # )
    
    # if success:
    #     print("数据处理并写入MySQL成功")
    # else:
    #     print("处理失败")

if __name__ == "__main__":
    print('-')

