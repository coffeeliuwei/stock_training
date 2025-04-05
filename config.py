import datetime as dt

# Tushare配置
TOKEN = ""  # 使用原项目的TOKEN
START_DATE = "2020-01-01"  # 数据起始日期
END_DATE = dt.datetime.now().strftime("%Y-%m-%d")  # 数据结束日期（当前日期）

# 数据存储路径
import os
# 使用绝对路径确保数据目录正确
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # 数据存储目录

# 可视化配置
DEFAULT_FIGSIZE = (12, 8)  # 默认图表大小
DEFAULT_STYLE = 'yahoo'  # K线图样式：'yahoo', 'charles', 'binance', 'ibd', 'classic'

# 技术指标配置
DEFAULT_INDICATORS = {
    'macd': True,  # MACD指标
    'rsi': True,   # RSI指标
    'kdj': True,   # KDJ指标
    'boll': True,  # 布林带
    'ma': [5, 10, 20, 30, 60]  # 移动平均线
}