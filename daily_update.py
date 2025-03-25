from StockDownloader.src.main import download_all_stock_data, download_all_index_data
from StockDownloader.src.core.logger import logger
import time
from datetime import datetime, timedelta
import akshare as ak
from functools import wraps
import random

def retry_with_delay(max_retries=3, initial_delay=60):
    """
    带重试和延迟的装饰器
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    logger.warning(f"操作失败，{delay}秒后重试: {str(e)}")
                    # 添加随机延迟，避免固定间隔
                    actual_delay = delay + random.randint(1, 30)
                    time.sleep(actual_delay)
                    # 增加下次重试的延迟时间
                    delay *= 2
            return None
        return wrapper
    return decorator

@retry_with_delay(max_retries=3, initial_delay=60)
def is_trading_day():
    """
    判断今天是否为交易日
    通过获取交易日历来判断
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        # 获取交易日历
        df = ak.tool_trade_date_hist_sina()
        # 将交易日历中的日期转换为字符串格式
        trade_dates = [d.strftime('%Y%m%d') for d in df['trade_date'].values]
        return today in trade_dates
    except Exception as e:
        logger.error(f"检查交易日时发生错误: {str(e)}")
        raise

@retry_with_delay(max_retries=3, initial_delay=300)  # 5分钟初始延迟
def update_stock_data():
    """
    更新股票数据，带重试机制
    """
    download_all_stock_data(update_only=True)

@retry_with_delay(max_retries=3, initial_delay=300)  # 5分钟初始延迟
def update_index_data():
    """
    更新指数数据，带重试机制
    """
    download_all_index_data(update_only=True)

def is_update_time_window():
    """
    检查是否在更新时间窗口内（23:00-03:00）
    """
    current_hour = datetime.now().hour
    return current_hour >= 23 or current_hour <= 3

def wait_until_next_check():
    """
    等待到第二天23:00
    """
    now = datetime.now()
    # 计算到第二天23:00的时间
    next_check = now.replace(hour=23, minute=0, second=0, microsecond=0)
    if now >= next_check:
        next_check += timedelta(days=1)
    
    wait_seconds = (next_check - now).total_seconds()
    logger.info(f"等待 {wait_seconds/3600:.2f} 小时到下次检查时间")
    time.sleep(wait_seconds)

def update_data():
    """
    执行数据更新任务
    """
    try:
        # 更新股票数据
        logger.info("开始更新股票日线数据...")
        update_stock_data()
        
        # 随机等待5-10分钟
        wait_time = random.randint(300, 600)
        logger.info(f"等待{wait_time}秒后开始更新指数日线数据...")
        time.sleep(wait_time)
        
        # 更新指数数据
        logger.info("开始更新指数日线数据...")
        update_index_data()
        
        logger.info("数据更新任务执行完成")
        return True
    except Exception as e:
        logger.error(f"数据更新过程中发生错误: {str(e)}")
        return False

def main():
    """
    主函数，执行每日数据更新任务
    """
    # 服务启动时立即执行一次更新
    logger.info("服务启动，执行首次数据更新...")
    update_data()
    logger.info("首次更新完成，进入计划任务模式")
    
    while True:
        try:
            # 1. 检查是否为交易日
            if not is_trading_day():
                logger.info("今天不是交易日，等待到明天23:00再次检查")
                wait_until_next_check()
                continue
                
            # 2. 检查是否在更新时间窗口内
            if not is_update_time_window():
                logger.info("不在更新时间窗口内（23:00-03:00），等待到明天23:00")
                wait_until_next_check()
                continue
            
            # 3. 执行更新任务
            # 注意：一旦开始更新，就让它完成，不会因为超出时间窗口而中断
            update_data()
            
            # 4. 等待到第二天23:00
            wait_until_next_check()
            
        except Exception as e:
            logger.error(f"执行过程中发生错误: {str(e)}")
            # 发生错误时等待较长时间后重试
            time.sleep(300)  # 5分钟

if __name__ == "__main__":
    main() 