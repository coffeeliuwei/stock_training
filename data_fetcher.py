import pandas as pd
import tushare as ts
import os
import logging
from datetime import datetime
from config import TOKEN, START_DATE, END_DATE, DATA_DIR, BASE_DIR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_fetcher')

# 初始化tushare
ts.set_token(TOKEN)
pro = ts.pro_api()


def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, 'daily'), exist_ok=True)


def format_date_str(date_str):
    """确保日期字符串格式正确"""
    # 处理numpy.int64类型
    if hasattr(date_str, 'item'):
        date_str = date_str.item()
    # 处理int类型
    if isinstance(date_str, (int, float)):
        date_str = str(int(date_str))
    # 处理字符串类型，确保格式为YYYYMMDD
    return str(date_str).replace('-', '')


def get_stock_basic():
    """获取股票列表数据（排除北交所）"""
    try:
        # 创建数据目录
        ensure_data_dir()
        
        # 获取全量股票列表
        df = pro.stock_basic(
            exchange='', 
            list_status='L',
            fields='ts_code,symbol,name,area,industry,market,list_date,is_hs,delist_date'
        )
        
        # 过滤条件：排除北交所 + 未退市
        df = df[(df['market'] != '北交所') & (df['delist_date'].isna())]
        
        # 保存数据
        if not df.empty:
            filename = os.path.join(DATA_DIR, "stock_basic.csv")
            df.to_csv(filename, index=False)
            logger.info(f"保存{len(df)}条股票数据到 {filename}")
        else:
            logger.warning("获取的股票列表为空")
            
        return df
    
    except Exception as e:
        logger.error(f"获取股票数据失败: {str(e)}")
        return pd.DataFrame()


def get_latest_trade_date(file_path):
    """获取已存数据的最新交易日期"""
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if not df.empty:
                # 确保trade_date列为字符串类型
                df['trade_date'] = df['trade_date'].astype(str)
                return df['trade_date'].max()
    except Exception as e:
        logger.error(f"读取文件{file_path}出错: {e}")
    return None


def get_daily_data(ts_code=None):
    """获取日线数据
    
    Args:
        ts_code: 股票代码，如果为None则获取所有股票的数据
    """
    # 创建存储目录
    ensure_data_dir()
    
    # 读取股票列表
    stock_list_file = os.path.join(DATA_DIR, 'stock_basic.csv')
    if not os.path.exists(stock_list_file):
        logger.info("股票列表文件不存在，正在获取...")
        get_stock_basic()
    
    stock_list = pd.read_csv(stock_list_file)
    
    # 确定要处理的股票列表
    if ts_code:
        if ts_code in stock_list['ts_code'].values:
            all_stocks = [ts_code]
        else:
            logger.error(f"股票代码 {ts_code} 不在列表中")
            return None
    else:
        all_stocks = stock_list['ts_code'].unique()
    
    # 转换日期格式
    end_date = format_date_str(END_DATE)
    
    # 分批处理股票（每次10个）
    results = {}
    for i in range(0, len(all_stocks), 10):
        batch = all_stocks[i:i+10]
        
        for ts_code in batch:
            file_path = os.path.join(DATA_DIR, 'daily', f'{ts_code}.csv')
            latest_date = get_latest_trade_date(file_path)
            
            if latest_date:
                # 增量更新：从最新日期后一天开始
                latest_date = format_date_str(latest_date)
                # 将字符串日期转为整数进行比较
                if int(latest_date) >= int(end_date):  # 数据已是最新
                    logger.info(f'{ts_code} 数据已是最新')
                    # 读取现有数据并返回
                    results[ts_code] = pd.read_csv(file_path)
                    continue
                start_date = format_date_str(str(int(latest_date) + 1))
            else:
                # 新股票：从START_DATE开始
                start_date = format_date_str(START_DATE)
            
            logger.info(f'正在下载 {ts_code} 从 {start_date} 到 {end_date} 的数据...')
            
            retry_count = 3  # 添加重试机制
            while retry_count > 0:
                try:
                    df = pro.daily(
                        ts_code=ts_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if not df.empty:
                        # 确保trade_date列为字符串类型
                        df['trade_date'] = df['trade_date'].astype(str)
                        
                        # 如果文件存在，读取并合并数据
                        if os.path.exists(file_path):
                            existing_data = pd.read_csv(file_path)
                            # 确保existing_data的trade_date也是字符串类型
                            existing_data['trade_date'] = existing_data['trade_date'].astype(str)
                            df = pd.concat([existing_data, df], ignore_index=True)
                        
                        # 去重和排序
                        df = df.drop_duplicates(
                            subset=['trade_date'],
                            keep='last'
                        ).sort_values('trade_date', ascending=True)
                        
                        # 保存数据
                        df.to_csv(
                            file_path,
                            mode='w',
                            header=True,
                            index=False
                        )
                        
                        logger.info(f'{ts_code} 数据下载完成，共 {len(df)} 条记录')
                        results[ts_code] = df
                        break
                    else:
                        logger.warning(f'{ts_code} 在指定日期范围内没有数据')
                        retry_count = 0  # 如果没有数据，不再重试
                        break
                        
                except Exception as e:
                    retry_count -= 1
                    if retry_count > 0:
                        logger.warning(f'{ts_code} 数据下载失败，剩余重试次数: {retry_count}，错误: {e}')
                    else:
                        logger.error(f'{ts_code} 数据下载失败，错误: {e}')
    
    return results


if __name__ == "__main__":
    # 测试代码
    print("获取股票基本信息...")
    stock_df = get_stock_basic()
    print(f"共获取到 {len(stock_df)} 只股票的基本信息")
    
    print("\n获取平安银行(000001.SZ)的日线数据...")
    daily_data = get_daily_data("000001.SZ")
    if daily_data and "000001.SZ" in daily_data:
        print(f"共获取到 {len(daily_data['000001.SZ'])} 条日线数据")
        print(daily_data["000001.SZ"].head())