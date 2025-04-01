import yfinance as yf
import pandas as pd

def get_stock_data(stock_code, start_date, end_date):
    """
    获取股票历史数据
    :param stock_code: 股票代码，例如 '600036.SS' (上海) 或 '000001.SZ' (深圳)
    :param start_date: 开始日期，格式 'YYYY-MM-DD'
    :param end_date: 结束日期，格式 'YYYY-MM-DD'
    :return: 包含开盘价、收盘价、成交量等数据的DataFrame
    """
    try:
        # 下载股票数据
        stock = yf.Ticker(stock_code)
        df = stock.history(start=start_date, end=end_date)
        
        # 选择需要的列
        df = df[['Open', 'Close', 'Volume']]
        df.columns = ['开盘价', '收盘价', '成交量']
        
        # 重置索引，将日期变为一列
        df.reset_index(inplace=True)
        
        return df
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

# 示例使用
if __name__ == "__main__":
    # 股票代码：贵州茅台（上海交易所）
    stock_code = "600519.SS"
    start_date = "2010-01-01"
    end_date = "2023-12-31"
    
    data = get_stock_data(stock_code, start_date, end_date)
    
    if data is not None:
        print(data.head())
        # 保存到CSV文件
        data.to_csv(f"{stock_code}_历史数据.csv", index=False, encoding='utf_8_sig')
        print("数据已保存到CSV文件")