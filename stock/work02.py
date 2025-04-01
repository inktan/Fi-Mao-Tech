
import requests
import pandas as pd
from datetime import datetime

def get_sina_stock_data(stock_code, start_date, end_date):
    """
    从新浪财经获取股票历史数据
    :param stock_code: 股票代码，例如 'sh600036' 或 'sz000001'
    :param start_date: 开始日期，格式 'YYYY-MM-DD'
    :param end_date: 结束日期，格式 'YYYY-MM-DD'
    :return: 包含开盘价、收盘价、成交量等数据的DataFrame
    """
    try:
        # 转换日期格式
        start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')
        end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')
        
        # 构造URL
        url = f"http://quotes.money.163.com/service/chddata.html?code={stock_code}&start={start}&end={end}&fields=TCLOSE;TOPEN;VOTURNOVER"
        
        # 获取数据
        response = requests.get(url)
        response.encoding = 'gb2312'  # 新浪返回的数据编码
        
        # 处理数据
        data = response.text.split('\n')[1:]  # 去掉标题行
        rows = []
        for line in data:
            if line.strip():
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    date = parts[0]
                    close = float(parts[3]) if parts[3] else None
                    open_ = float(parts[6]) if parts[6] else None
                    volume = float(parts[7]) if parts[7] else None
                    rows.append([date, open_, close, volume])
        
        # 创建DataFrame
        df = pd.DataFrame(rows, columns=['日期', '开盘价', '收盘价', '成交量'])
        return df
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

# 示例使用
if __name__ == "__main__":
    # 股票代码：贵州茅台（上海交易所）
    stock_code = "0600519"  # 新浪格式：0+股票代码
    start_date = "2010-01-01"
    end_date = "2023-12-31"
    
    data = get_sina_stock_data(stock_code, start_date, end_date)
    
    if data is not None:
        print(data.head())
        # 保存到CSV文件
        data.to_csv(f"{stock_code}_历史数据.csv", index=False, encoding='utf_8_sig')
        print("数据已保存到CSV文件")