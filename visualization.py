import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import logging
from datetime import datetime, timedelta
from config import DEFAULT_FIGSIZE, DEFAULT_STYLE, DEFAULT_INDICATORS, DATA_DIR
from data_processor import get_stock_name

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('visualization')


def plot_candlestick(df, title=None, volume=True, savefig=None, show_figure=True):
    """
    绘制K线图
    
    Args:
        df: 包含OHLCV数据的DataFrame，索引为日期
        title: 图表标题，默认为None
        volume: 是否显示成交量，默认为True
        savefig: 保存图表的文件路径，默认为None（不保存）
        show_figure: 是否显示图表，默认为True
        
    Returns:
        fig: matplotlib图表对象
        ax: matplotlib轴对象
    """
    if df is None or df.empty:
        logger.error("数据为空，无法绘制K线图")
        return None, None
    
    # 设置图表样式
    mc = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='inherit',
        wick='inherit',
        volume='inherit'
    )
    
    s = mpf.make_mpf_style(
        base_mpf_style=DEFAULT_STYLE,
        marketcolors=mc
    )
    
    # 设置图表参数
    kwargs = {
        'type': 'candle',
        'style': s,
        'figsize': DEFAULT_FIGSIZE,
        'title': title,
        'returnfig': True
    }
    
    # 添加成交量
    if volume and 'volume' in df.columns:
        kwargs['volume'] = True
        kwargs['panel_ratios'] = (4, 1)  # 主图和成交量图的比例
    
    # 绘制K线图
    fig, axes = mpf.plot(df, **kwargs)
    
    # 保存图表
    if savefig:
        plt.savefig(savefig)
        logger.info(f"图表已保存至 {savefig}")
    
    # 显示图表
    if show_figure:
        plt.show()
    
    return fig, axes


def plot_with_indicators(df, title=None, indicators=None, savefig=None, show_figure=True):
    """
    绘制带有技术指标的K线图
    
    Args:
        df: 包含OHLCV和技术指标数据的DataFrame，索引为日期
        title: 图表标题，默认为None
        indicators: 要显示的指标字典，默认使用config中的DEFAULT_INDICATORS
        savefig: 保存图表的文件路径，默认为None（不保存）
        show_figure: 是否显示图表，默认为True
        
    Returns:
        fig: matplotlib图表对象
        axes: matplotlib轴对象列表
    """
    if df is None or df.empty:
        logger.error("数据为空，无法绘制K线图")
        return None, None
    
    # 使用默认指标配置（如果未指定）
    if indicators is None:
        indicators = DEFAULT_INDICATORS
    
    # 设置图表样式
    mc = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='inherit',
        wick='inherit',
        volume='inherit'
    )
    
    s = mpf.make_mpf_style(
        base_mpf_style=DEFAULT_STYLE,
        marketcolors=mc
    )
    
    # 准备附加图表
    panels = []
    
    # 添加成交量面板
    if 'volume' in df.columns:
        panels.append({
            'panel': 1,
            'ylabel': '成交量',
            'mav': (5, 10) if 'volume_ma5' in df.columns and 'volume_ma10' in df.columns else None
        })
    
    # 添加MACD指标
    if indicators.get('macd', False) and 'macd' in df.columns:
        panels.append({
            'panel': 2,
            'ylabel': 'MACD',
            'secondary_y': False,
            'type': 'line',
            'mav': None
        })
    
    # 添加RSI指标
    if indicators.get('rsi', False) and 'rsi' in df.columns:
        panels.append({
            'panel': 3,
            'ylabel': 'RSI',
            'secondary_y': False,
            'type': 'line',
            'mav': None
        })
    
    # 添加KDJ指标
    if indicators.get('kdj', False) and 'kdj_k' in df.columns:
        panels.append({
            'panel': 4,
            'ylabel': 'KDJ',
            'secondary_y': False,
            'type': 'line',
            'mav': None
        })
    
    # 计算面板数量和比例
    num_panels = len(panels) + 1  # +1 是因为主K线图
    panel_ratios = tuple([4] + [1] * (num_panels - 1))  # 主图占4份，其他各占1份
    
    # 设置图表参数
    kwargs = {
        'type': 'candle',
        'style': s,
        'figsize': (DEFAULT_FIGSIZE[0], DEFAULT_FIGSIZE[1] * num_panels / 2),  # 根据面板数量调整高度
        'title': title,
        'volume': 'volume' in df.columns,
        'panel_ratios': panel_ratios,
        'returnfig': True
    }
    
    # 添加移动平均线
    if indicators.get('ma', False):
        ma_periods = indicators['ma'] if isinstance(indicators['ma'], list) else [5, 10, 20, 30, 60]
        addplot = []
        colors = ['blue', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        
        for i, period in enumerate(ma_periods):
            if f'ma{period}' in df.columns:
                addplot.append(
                    mpf.make_addplot(
                        df[f'ma{period}'],
                        panel=0,
                        color=colors[i % len(colors)],
                        secondary_y=False
                    )
                )
        
        # 添加MACD指标线
        if indicators.get('macd', False) and 'macd' in df.columns:
            addplot.append(mpf.make_addplot(df['macd'], panel=2, color='blue', secondary_y=False))
            addplot.append(mpf.make_addplot(df['macd_signal'], panel=2, color='red', secondary_y=False))
            addplot.append(mpf.make_addplot(df['macd_hist'], panel=2, color='green', type='bar', secondary_y=False))
        
        # 添加RSI指标线
        if indicators.get('rsi', False) and 'rsi' in df.columns:
            addplot.append(mpf.make_addplot(df['rsi'], panel=3, color='purple', secondary_y=False))
            # 添加RSI的30和70线
            addplot.append(mpf.make_addplot([30] * len(df), panel=3, color='red', linestyle='--', secondary_y=False))
            addplot.append(mpf.make_addplot([70] * len(df), panel=3, color='red', linestyle='--', secondary_y=False))
        
        # 添加KDJ指标线
        if indicators.get('kdj', False) and 'kdj_k' in df.columns:
            addplot.append(mpf.make_addplot(df['kdj_k'], panel=4, color='blue', secondary_y=False))
            addplot.append(mpf.make_addplot(df['kdj_d'], panel=4, color='red', secondary_y=False))
            addplot.append(mpf.make_addplot(df['kdj_j'], panel=4, color='green', secondary_y=False))
        
        # 添加布林带
        if indicators.get('boll', False) and 'boll_upper' in df.columns:
            addplot.append(mpf.make_addplot(df['boll_upper'], panel=0, color='gray', linestyle='--', secondary_y=False))
            addplot.append(mpf.make_addplot(df['boll_mid'], panel=0, color='gray', secondary_y=False))
            addplot.append(mpf.make_addplot(df['boll_lower'], panel=0, color='gray', linestyle='--', secondary_y=False))
        
        kwargs['addplot'] = addplot
    
    # 绘制K线图
    fig, axes = mpf.plot(df, **kwargs)
    
    # 保存图表
    if savefig:
        plt.savefig(savefig)
        logger.info(f"图表已保存至 {savefig}")
    
    # 显示图表
    if show_figure:
        plt.show()
    
    return fig, axes


def plot_stock(ts_code, start_date=None, end_date=None, indicators=None, savefig=None, show_figure=True):
    """
    绘制股票K线图和技术指标
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期，格式为'YYYY-MM-DD'，如果为None则使用最近一年的数据
        end_date: 结束日期，格式为'YYYY-MM-DD'，如果为None则使用当前日期
        indicators: 要显示的指标字典
        savefig: 保存图表的文件路径
        show_figure: 是否显示图表
        
    Returns:
        fig: matplotlib图表对象
        axes: matplotlib轴对象列表
    """
    from data_processor import prepare_data_for_visualization
    from indicators import calculate_all_indicators
    
    # 如果未指定开始日期，则使用最近一年的数据
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 如果未指定结束日期，则使用当前日期
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 准备数据
    df = prepare_data_for_visualization(ts_code, start_date, end_date)
    if df is None or df.empty:
        logger.error(f"无法获取股票 {ts_code} 的数据")
        return None, None
    
    # 计算技术指标
    df = calculate_all_indicators(df)
    
    # 获取股票名称
    stock_name = get_stock_name(ts_code)
    title = f"{stock_name}({ts_code}) K线图 {start_date} 至 {end_date}"
    
    # 绘制图表
    return plot_with_indicators(df, title, indicators, savefig, show_figure)


def save_plot_to_html(ts_code, start_date=None, end_date=None, output_dir=None):
    # 使用绝对路径设置输出目录
    if output_dir is None:
        from config import BASE_DIR
        output_dir = os.path.join(BASE_DIR, 'charts')
    """
    将股票K线图保存为HTML文件
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期
        end_date: 结束日期
        output_dir: 输出目录
        
    Returns:
        str: HTML文件路径
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        from data_processor import prepare_data_for_visualization
        from indicators import calculate_all_indicators
        
        # 如果未指定开始日期，则使用最近一年的数据
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 如果未指定结束日期，则使用当前日期
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # 准备数据
        df = prepare_data_for_visualization(ts_code, start_date, end_date)
        if df is None or df.empty:
            logger.error(f"无法获取股票 {ts_code} 的数据")
            return None
        
        # 计算技术指标
        df = calculate_all_indicators(df)
        
        # 获取股票名称
        stock_name = get_stock_name(ts_code)
        title = f"{stock_name}({ts_code}) K线图 {start_date} 至 {end_date}"
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.7, 0.3],
            subplot_titles=(title, '成交量')
        )
        
        # 添加K线图
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K线'
            ),
            row=1, col=1
        )
        
        # 添加移动平均线
        for period in [5, 10, 20, 30, 60]:
            if f'ma{period}' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[f'ma{period}'],
                        name=f'MA{period}',
                        line=dict(width=1)
                    ),
                    row=1, col=1
                )
        
        # 添加成交量
        colors = ['red' if row['close'] >= row['open'] else 'green' for _, row in df.iterrows()]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['volume'],
                name='成交量',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        # 更新布局
        fig.update_layout(
            height=800,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存为HTML文件
        html_path = os.path.join(output_dir, f"{ts_code}_{start_date}_{end_date}.html")
        fig.write_html(html_path)
        logger.info(f"图表已保存至 {html_path}")
        
        return html_path
    
    except Exception as e:
        logger.error(f"保存HTML图表时出错: {e}")
        return None


if __name__ == "__main__":
    # 测试代码
    from data_processor import prepare_data_for_visualization
    from indicators import calculate_all_indicators
    
    ts_code = "000001.SZ"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    print(f"绘制 {ts_code} 从 {start_date} 到 {end_date} 的K线图...")
    
    # 准备数据
    df = prepare_data_for_visualization(ts_code, start_date, end_date)
    if df is not None:
        # 计算技术指标
        df = calculate_all_indicators(df)
        
        # 绘制基本K线图
        stock_name = get_stock_name(ts_code)
        title = f"{stock_name}({ts_code}) K线图 {start_date} 至 {end_date}"
        plot_candlestick(df, title)
        
        # 绘制带有技术指标的K线图
        plot_with_indicators(df, title)
        
        # 使用便捷函数绘制
        plot_stock(ts_code, start_date, end_date)
        
        # 保存为HTML
        html_path = save_plot_to_html(ts_code, start_date, end_date)
        if html_path:
            print(f"HTML图表已保存至: {html_path}")
    else:
        print(f"无法获取 {ts_code} 的数据")