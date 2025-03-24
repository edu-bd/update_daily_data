from StockDownloader.src.main import download_all_stock_data, download_all_index_data
from StockDownloader.src.core.logger import logger
import time

def main():
    """
    主函数，执行每日数据更新任务
    """
    try:
        logger.info("开始执行每日数据更新任务...")
        
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