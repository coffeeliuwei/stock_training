import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from config import DATA_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_processor')


def load_stock_data(ts_code):
    """加载指定股票的日线数据
    
    Args:
        ts_code: 股票代码，如'000001.SZ'
        
    Returns:
        DataFrame: 股票日线数据，如果文件不存在则返回None
    """
    file_path = os.path.join(DATA_DIR, 'daily', f'{ts_code}.csv')
    if not os.path.exists(file_path):
        logger.warning(f"股票 {ts_code} 的数据文件不存在")
        return None
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logger.error(f"读取股票 {ts_code} 数据失败: {e}")
        return None


def process_stock_data(df):
    """处理股票数据，进行必要的转换和清洗
    
    Args:
        df: 原始股票数据DataFrame
        
    Returns:
        DataFrame: 处理后的数据
    """
    if df is None or df.empty:
        return None
    
    # 创建副本，避免修改原始数据
    df = df.copy()
    
    # 转换日期格式
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    
    # 设置日期为索引
    df.set_index('trade_date', inplace=True)
    
    # 按日期排序
    df.sort_index(inplace=True)
    
    # 处理缺失值
    df.fillna(method='ffill', inplace=True)  # 用前一个值填充
    
    # 确保数值类型正确
    numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def prepare_data_for_visualization(ts_code, start_date=None, end_date=None):
    """准备用于可视化的数据
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期，格式为'YYYY-MM-DD'，如果为None则使用全部数据
        end_date: 结束日期，格式为'YYYY-MM-DD'，如果为None则使用全部数据
        
    Returns:
        DataFrame: 处理后的数据，适合用于绘制K线图
    """
    # 加载数据
    df = load_stock_data(ts_code)
    if df is None:
        return None
    
    # 处理数据
    df = process_stock_data(df)
    if df is None:
        return None
    
    # 筛选日期范围
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df.index >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        df = df[df.index <= end_date]
    
    # 重命名列以适应mplfinance的要求
    df_ohlcv = df[['open', 'high', 'low', 'close', 'vol']].copy()
    df_ohlcv.rename(columns={'vol': 'volume'}, inplace=True)
    
    return df_ohlcv


def get_stock_name(ts_code):
    """根据股票代码获取股票名称
    
    Args:
        ts_code: 股票代码
        
    Returns:
        str: 股票名称
    """
    stock_basic_path = os.path.join(DATA_DIR, 'stock_basic.csv')
    if not os.path.exists(stock_basic_path):
        logger.warning("股票基本信息文件不存在")
        return ts_code
    
    try:
        stock_basic = pd.read_csv(stock_basic_path)
        stock_info = stock_basic[stock_basic['ts_code'] == ts_code]
        if not stock_info.empty:
            return stock_info.iloc[0]['name']
        else:
            return ts_code
    except Exception as e:
        logger.error(f"获取股票名称失败: {e}")
        return ts_code


if __name__ == "__main__":
    # 测试代码
    ts_code = "000001.SZ"
    print(f"加载并处理 {ts_code} 的数据...")
    
    df = load_stock_data(ts_code)
    if df is not None:
        print(f"原始数据前5行:\n{df.head()}")
        
        processed_df = process_stock_data(df)
        print(f"\n处理后数据前5行:\n{processed_df.head()}")
        
        viz_data = prepare_data_for_visualization(ts_code, '2023-01-01', '2023-12-31')
        print(f"\n可视化数据前5行:\n{viz_data.head()}")
        
        stock_name = get_stock_name(ts_code)
        print(f"\n股票名称: {stock_name}")
    else:
        print(f"无法加载 {ts_code} 的数据")