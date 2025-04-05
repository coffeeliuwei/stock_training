import pandas as pd
import numpy as np
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('indicators')


def calculate_ma(df, periods=[5, 10, 20, 30, 60]):
    """
    计算移动平均线
    
    Args:
        df: 包含'close'列的DataFrame
        periods: 移动平均的周期列表，默认为[5, 10, 20, 30, 60]
        
    Returns:
        DataFrame: 添加了移动平均线的DataFrame
    """
    result = df.copy()
    for period in periods:
        result[f'ma{period}'] = result['close'].rolling(window=period).mean()
    return result


def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    计算MACD指标
    
    Args:
        df: 包含'close'列的DataFrame
        fast_period: 快线周期，默认为12
        slow_period: 慢线周期，默认为26
        signal_period: 信号线周期，默认为9
        
    Returns:
        DataFrame: 添加了MACD指标的DataFrame
    """
    result = df.copy()
    
    # 计算快线和慢线的指数移动平均
    ema_fast = result['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = result['close'].ewm(span=slow_period, adjust=False).mean()
    
    # 计算MACD线和信号线
    result['macd'] = ema_fast - ema_slow
    result['macd_signal'] = result['macd'].ewm(span=signal_period, adjust=False).mean()
    
    # 计算MACD柱状图
    result['macd_hist'] = result['macd'] - result['macd_signal']
    
    return result


def calculate_rsi(df, periods=14):
    """
    计算RSI指标
    
    Args:
        df: 包含'close'列的DataFrame
        periods: RSI周期，默认为14
        
    Returns:
        DataFrame: 添加了RSI指标的DataFrame
    """
    result = df.copy()
    
    # 计算价格变化
    delta = result['close'].diff()
    
    # 分离上涨和下跌
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # 计算平均上涨和下跌
    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()
    
    # 计算相对强度
    rs = avg_gain / avg_loss
    
    # 计算RSI
    result['rsi'] = 100 - (100 / (1 + rs))
    
    return result


def calculate_kdj(df, k_period=9, d_period=3, j_period=3):
    """
    计算KDJ指标
    
    Args:
        df: 包含'high', 'low', 'close'列的DataFrame
        k_period: K线周期，默认为9
        d_period: D线周期，默认为3
        j_period: J线周期，默认为3
        
    Returns:
        DataFrame: 添加了KDJ指标的DataFrame
    """
    result = df.copy()
    
    # 计算最低价和最高价
    low_min = result['low'].rolling(window=k_period).min()
    high_max = result['high'].rolling(window=k_period).max()
    
    # 计算RSV
    rsv = 100 * ((result['close'] - low_min) / (high_max - low_min))
    
    # 计算K值、D值和J值
    result['kdj_k'] = rsv.ewm(alpha=1/d_period, adjust=False).mean()
    result['kdj_d'] = result['kdj_k'].ewm(alpha=1/j_period, adjust=False).mean()
    result['kdj_j'] = 3 * result['kdj_k'] - 2 * result['kdj_d']
    
    return result


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """
    计算布林带指标
    
    Args:
        df: 包含'close'列的DataFrame
        period: 移动平均周期，默认为20
        std_dev: 标准差倍数，默认为2
        
    Returns:
        DataFrame: 添加了布林带指标的DataFrame
    """
    result = df.copy()
    
    # 计算移动平均线
    result['boll_mid'] = result['close'].rolling(window=period).mean()
    
    # 计算标准差
    result['boll_std'] = result['close'].rolling(window=period).std()
    
    # 计算上轨和下轨
    result['boll_upper'] = result['boll_mid'] + (result['boll_std'] * std_dev)
    result['boll_lower'] = result['boll_mid'] - (result['boll_std'] * std_dev)
    
    return result


def calculate_volume_ma(df, periods=[5, 10, 20]):
    """
    计算成交量移动平均线
    
    Args:
        df: 包含'volume'列的DataFrame
        periods: 移动平均的周期列表，默认为[5, 10, 20]
        
    Returns:
        DataFrame: 添加了成交量移动平均线的DataFrame
    """
    result = df.copy()
    for period in periods:
        result[f'volume_ma{period}'] = result['volume'].rolling(window=period).mean()
    return result


def calculate_all_indicators(df):
    """
    计算所有技术指标
    
    Args:
        df: 包含OHLCV数据的DataFrame
        
    Returns:
        DataFrame: 添加了所有技术指标的DataFrame
    """
    try:
        # 确保DataFrame包含所需的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"DataFrame缺少必要的列: {col}")
                return df
        
        # 计算各种指标
        result = df.copy()
        result = calculate_ma(result)
        result = calculate_macd(result)
        result = calculate_rsi(result)
        result = calculate_kdj(result)
        result = calculate_bollinger_bands(result)
        result = calculate_volume_ma(result)
        
        return result
    
    except Exception as e:
        logger.error(f"计算技术指标时出错: {e}")
        return df


if __name__ == "__main__":
    # 测试代码
    from data_processor import load_stock_data, process_stock_data
    
    ts_code = "000001.SZ"
    print(f"加载并处理 {ts_code} 的数据...")
    
    df = load_stock_data(ts_code)
    if df is not None:
        processed_df = process_stock_data(df)
        
        # 计算所有指标
        indicators_df = calculate_all_indicators(processed_df)
        
        # 显示结果
        print(f"计算后的指标数据前5行:\n{indicators_df.head()}")
        print(f"\n数据列: {indicators_df.columns.tolist()}")
    else:
        print(f"无法加载 {ts_code} 的数据")