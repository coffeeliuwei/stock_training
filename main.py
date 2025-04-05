import argparse
import os
import logging
from datetime import datetime, timedelta

# 导入项目模块
from data_fetcher import get_stock_basic, get_daily_data
from data_processor import prepare_data_for_visualization, get_stock_name
from indicators import calculate_all_indicators
from visualization import plot_stock, save_plot_to_html
from config import DATA_DIR, BASE_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('main')


def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'daily'), exist_ok=True)
    # 使用绝对路径创建charts目录
    charts_dir = os.path.join(BASE_DIR, 'charts')
    os.makedirs(charts_dir, exist_ok=True)


def fetch_data(ts_code=None, update_stock_list=False):
    """获取数据
    
    Args:
        ts_code: 股票代码，如果为None则获取所有股票的数据
        update_stock_list: 是否更新股票列表
    """
    # 确保数据目录存在
    ensure_data_dir()
    
    # 获取/更新股票列表
    if update_stock_list or not os.path.exists(os.path.join(DATA_DIR, 'stock_basic.csv')):
        logger.info("获取股票基本信息...")
        stock_df = get_stock_basic()
        logger.info(f"共获取到 {len(stock_df)} 只股票的基本信息")
    
    # 获取日线数据
    if ts_code:
        logger.info(f"获取 {ts_code} 的日线数据...")
        daily_data = get_daily_data(ts_code)
        if daily_data and ts_code in daily_data:
            logger.info(f"共获取到 {len(daily_data[ts_code])} 条日线数据")
        else:
            logger.error(f"获取 {ts_code} 的日线数据失败")
    else:
        logger.info("获取所有股票的日线数据...")
        daily_data = get_daily_data()
        logger.info(f"共获取到 {len(daily_data)} 只股票的日线数据")


def visualize_stock(ts_code, start_date=None, end_date=None, save_html=False):
    """可视化股票数据
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期，格式为'YYYY-MM-DD'
        end_date: 结束日期，格式为'YYYY-MM-DD'
        save_html: 是否保存为HTML文件
    """
    # 如果未指定开始日期，则使用最近一年的数据
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 如果未指定结束日期，则使用当前日期
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 获取股票名称
    stock_name = get_stock_name(ts_code)
    logger.info(f"可视化 {stock_name}({ts_code}) 从 {start_date} 到 {end_date} 的数据...")
    
    # 绘制K线图和技术指标
    plot_stock(ts_code, start_date, end_date)
    
    # 保存为HTML文件
    if save_html:
        html_path = save_plot_to_html(ts_code, start_date, end_date)
        if html_path:
            logger.info(f"HTML图表已保存至: {html_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='股票数据获取与可视化工具')
    
    # 添加命令行参数
    parser.add_argument('--fetch', action='store_true', help='获取数据')
    parser.add_argument('--visualize', action='store_true', help='可视化数据')
    parser.add_argument('--code', type=str, help='股票代码，如000001.SZ')
    parser.add_argument('--start', type=str, help='开始日期，格式为YYYY-MM-DD')
    parser.add_argument('--end', type=str, help='结束日期，格式为YYYY-MM-DD')
    parser.add_argument('--update-list', action='store_true', help='更新股票列表')
    parser.add_argument('--save-html', action='store_true', help='保存为HTML文件')
    
    args = parser.parse_args()
    
    # 确保数据目录存在
    ensure_data_dir()
    
    # 获取数据
    if args.fetch:
        fetch_data(args.code, args.update_list)
    
    # 可视化数据
    if args.visualize:
        if args.code:
            visualize_stock(args.code, args.start, args.end, args.save_html)
        else:
            logger.error("可视化数据需要指定股票代码，请使用--code参数")
    
    # 如果没有指定任何操作，显示帮助信息
    if not (args.fetch or args.visualize):
        parser.print_help()


def demo():
    """演示函数"""
    # 确保数据目录存在
    ensure_data_dir()
    
    # 获取股票列表
    if not os.path.exists(os.path.join(DATA_DIR, 'stock_basic.csv')):
        logger.info("获取股票基本信息...")
        get_stock_basic()
    
    # 获取平安银行的日线数据
    ts_code = "000001.SZ"
    logger.info(f"获取 {ts_code} 的日线数据...")
    get_daily_data(ts_code)
    
    # 可视化平安银行的K线图和技术指标
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    logger.info(f"可视化 {ts_code} 从 {start_date} 到 {end_date} 的数据...")
    plot_stock(ts_code, start_date, end_date)
    
    # 保存为HTML文件
    html_path = save_plot_to_html(ts_code, start_date, end_date)
    if html_path:
        logger.info(f"HTML图表已保存至: {html_path}")


if __name__ == "__main__":
    main()
    # 如果想运行演示，取消下面的注释
    # demo()