from StockDownloader.src.main import download_all_stock_data, download_all_index_data
from StockDownloader.src.core.logger import logger
import time
from datetime import datetime, timedelta
import akshare as ak

def is_trading_day():
    """
    判断今天是否为交易日
    通过检查今天是否有股票数据来判断
    """
    try:
        today = datetime.now().strftime('%Y%m%d')
        # 尝试获取上证指数当天的数据
        df = ak.stock_zh_index_daily(symbol="sh000001")
        latest_date = df['date'].iloc[0]
        return latest_date == today
    except Exception as e:
        logger.error(f"检查交易日时发生错误: {str(e)}")
        return False

def main():
    """
    主函数，执行每日数据更新任务
    """
    try:
        logger.info("开始检查是否为交易日...")
        
        # 检查今天是否为交易日
        if not is_trading_day():
            logger.info("今天不是交易日，跳过数据更新")
            return
            
        logger.info("确认今天是交易日，开始执行数据更新任务...")
        
        # 更新股票日线数据
        logger.info("开始更新股票日线数据...")
        download_all_stock_data(update_only=True)
        logger.info("股票日线数据更新完成")
        
        # 等待1分钟后更新指数数据
        logger.info("等待1分钟后开始更新指数日线数据...")
        time.sleep(60)
        
        # 更新指数日线数据
        logger.info("开始更新指数日线数据...")
        download_all_index_data(update_only=True)
        logger.info("指数日线数据更新完成")
        
        logger.info("每日数据更新任务执行完成")
        
    except Exception as e:
        logger.error(f"数据更新过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main() 