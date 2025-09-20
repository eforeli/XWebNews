#!/usr/bin/env python3
"""
Zeabur 排程器 - 替代 cron job 的解決方案
每分鐘檢查是否到了執行時間（每天早上8點台灣時間）
"""

import time
import subprocess
import logging
import os
from datetime import datetime
import pytz

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def is_execution_time():
    """檢查是否為執行時間（每天早上8點台灣時間）"""
    taipei_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(taipei_tz)
    
    # 檢查是否為早上8點的第一分鐘
    if now.hour == 8 and now.minute == 0:
        return True
    return False

def has_run_today():
    """檢查今天是否已經執行過"""
    taipei_tz = pytz.timezone('Asia/Taipei')
    today = datetime.now(taipei_tz).strftime('%Y-%m-%d')
    try:
        with open('last_run.txt', 'r') as f:
            last_run = f.read().strip()
            return last_run == today
    except FileNotFoundError:
        return False

def mark_as_run():
    """標記今天已執行"""
    taipei_tz = pytz.timezone('Asia/Taipei')
    today = datetime.now(taipei_tz).strftime('%Y-%m-%d')
    with open('last_run.txt', 'w') as f:
        f.write(today)

def run_crawler():
    """執行爬蟲"""
    try:
        logger.info("開始執行爬蟲...")
        result = subprocess.run(
            ['python3', 'rotational_crawler.py'],
            capture_output=True,
            text=True,
            timeout=1800  # 30分鐘超時
        )
        
        if result.returncode == 0:
            logger.info("爬蟲執行成功")
            mark_as_run()
        else:
            logger.error(f"爬蟲執行失敗: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        logger.error("爬蟲執行超時")
    except Exception as e:
        logger.error(f"爬蟲執行異常: {e}")

def main():
    """主循環 - 每分鐘檢查一次"""
    logger.info("排程器啟動")
    
    while True:
        try:
            taipei_tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(taipei_tz)
            
            if is_execution_time() and not has_run_today():
                logger.info("到達執行時間，開始爬蟲...")
                run_crawler()
            elif current_time.hour == 8 and current_time.minute == 0:
                if has_run_today():
                    logger.info(f"今日已執行過爬蟲，跳過 (當前時間: {current_time.strftime('%H:%M')})")
            
            # 每60秒檢查一次
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("排程器停止")
            break
        except Exception as e:
            logger.error(f"排程器錯誤: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()