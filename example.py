# 股票数据分析示例脚本
# 本脚本展示如何使用实训项目的各个模块进行股票数据获取、分析和可视化

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 导入项目模块
from data_fetcher import get_stock_basic, get_daily_data
from data_processor import prepare_data_for_visualization, get_stock_name
from indicators import calculate_all_indicators, calculate_macd, calculate_rsi, calculate_kdj, calculate_bollinger_bands
from visualization import plot_candlestick, plot_with_indicators, plot_stock, save_plot_to_html
from config import DATA_DIR, BASE_DIR

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, 'daily'), exist_ok=True)
# 使用绝对路径创建charts目录
charts_dir = os.path.join(BASE_DIR, 'charts')
os.makedirs(charts_dir, exist_ok=True)

# 步骤1: 获取股票基本信息
print("步骤1: 获取股票基本信息")
if not os.path.exists(os.path.join(DATA_DIR, 'stock_basic.csv')):
    print("正在获取股票列表...")
    stock_df = get_stock_basic()
    print(f"共获取到 {len(stock_df)} 只股票的基本信息")
else:
    print("股票列表已存在，读取现有数据")
    stock_df = pd.read_csv(os.path.join(DATA_DIR, 'stock_basic.csv'))
    print(f"共有 {len(stock_df)} 只股票")

# 步骤2: 获取特定股票的日线数据
print("\n步骤2: 获取特定股票的日线数据")
ts_code = "000001.SZ"  # 平安银行
stock_name = get_stock_name(ts_code)
print(f"获取 {stock_name}({ts_code}) 的日线数据...")

# 检查数据是否已存在
data_file = os.path.join(DATA_DIR, 'daily', f'{ts_code}.csv')
if not os.path.exists(data_file):
    print("数据不存在，正在下载...")
    daily_data = get_daily_data(ts_code)
    if daily_data and ts_code in daily_data:
        print(f"成功获取 {len(daily_data[ts_code])} 条日线数据")
else:
    print("数据已存在，无需重新下载")

# 步骤3: 数据处理与准备
print("\n步骤3: 数据处理与准备")
# 设置日期范围 - 最近一年的数据
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
print(f"处理 {start_date} 至 {end_date} 的数据")

# 准备数据
df = prepare_data_for_visualization(ts_code, start_date, end_date)
if df is not None:
    print(f"成功准备 {len(df)} 条数据记录")
    print("数据预览:")
    print(df.head())
else:
    print("数据准备失败")
    exit(1)

# 步骤4: 计算技术指标
print("\n步骤4: 计算技术指标")
# 计算所有指标
df_all = calculate_all_indicators(df)
print("计算完成的指标:")
print([col for col in df_all.columns if col not in df.columns])

# 单独计算各指标示例
print("\n单独计算各指标示例:")
# MACD指标
df_macd = calculate_macd(df)
print("MACD指标列:")
print([col for col in df_macd.columns if col not in df.columns])

# RSI指标
df_rsi = calculate_rsi(df)
print("RSI指标列:")
print([col for col in df_rsi.columns if col not in df.columns])

# KDJ指标
df_kdj = calculate_kdj(df)
print("KDJ指标列:")
print([col for col in df_kdj.columns if col not in df.columns])

# 布林带指标
df_boll = calculate_bollinger_bands(df)
print("布林带指标列:")
print([col for col in df_boll.columns if col not in df.columns])

# 步骤5: 可视化 - 基本K线图
print("\n步骤5: 可视化 - 基本K线图")
print("绘制基本K线图...")
title = f"{stock_name}({ts_code}) K线图 {start_date} 至 {end_date}"
plot_candlestick(df, title, show_figure=False)

# 步骤6: 可视化 - 带技术指标的K线图
print("\n步骤6: 可视化 - 带技术指标的K线图")
print("绘制带技术指标的K线图...")
plot_with_indicators(df_all, title, show_figure=False)

# 步骤7: 使用便捷函数绘制完整图表
print("\n步骤7: 使用便捷函数绘制完整图表")
print("绘制完整K线图与技术指标...")
plot_stock(ts_code, start_date, end_date, show_figure=True)

# 步骤8: 保存为HTML交互式图表
print("\n步骤8: 保存为HTML交互式图表")
print("生成交互式HTML图表...")
html_path = save_plot_to_html(ts_code, start_date, end_date)
if html_path:
    print(f"HTML图表已保存至: {html_path}")
    print(f"请在浏览器中打开此文件查看交互式图表")

print("\n示例运行完成!")
print("您可以尝试修改股票代码、日期范围或技术指标参数来进行更多实验")