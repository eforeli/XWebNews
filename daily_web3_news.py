#!/usr/bin/env python3
"""
Daily Web3 News Pipeline
每日Web3新聞自動化流程：Twitter爬蟲 → OpenAI分析 → LINE推播
"""

import sys
import os
import logging
from datetime import datetime
from twitter_smart_crawler import SmartWeb3Crawler
from news_reporter import Web3NewsReporter
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def setup_logging():
    """設置日誌"""
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = f"daily_news_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_daily_pipeline():
    """執行每日新聞流程"""
    
    logger = setup_logging()
    logger.info("🚀 開始執行每日Web3新聞流程...")
    
    # ===== 設定參數 =====
    # Twitter API設定
    TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    # OpenAI和LINE設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'your_line_channel_access_token_here')
    LINE_USER_ID = os.getenv('LINE_USER_ID', 'your_line_user_id_here')
    
    # 檢查參數設定
    if (OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE" or 
        LINE_ACCESS_TOKEN == "YOUR_LINE_ACCESS_TOKEN_HERE" or
        LINE_USER_ID == "YOUR_LINE_USER_ID_HERE"):
        
        logger.error("❌ 請先設定OpenAI和LINE API參數")
        logger.info("請編輯此文件，填入以下參數：")
        logger.info("- OPENAI_API_KEY")  
        logger.info("- LINE_ACCESS_TOKEN")
        logger.info("- LINE_USER_ID")
        logger.info("或執行 python3 test_apis.py 自動設定")
        return False
    
    success_count = 0
    total_steps = 3
    
    try:
        # ===== 步驟1：智能爬取Twitter數據 =====
        logger.info("📊 步驟1/3：智能爬取Twitter精選內容...")
        
        crawler = SmartWeb3Crawler(TWITTER_BEARER_TOKEN)
        tweets_data = crawler.crawl_by_priority()  # 使用智能優先級爬取
        
        if not any(tweets for tweets in tweets_data.values()):
            logger.warning("⚠️  未爬取到任何推文數據，可能受到API限制")
            # 嘗試加載之前的智能爬取數據
            import glob
            import os
            json_files = glob.glob("smart_web3_tweets_*.json") + glob.glob("web3_tweets_*.json")
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                logger.info(f"使用之前的數據文件: {latest_file}")
                import json
                with open(latest_file, 'r', encoding='utf-8') as f:
                    tweets_data = json.load(f)
            else:
                logger.error("❌ 沒有可用的推文數據")
                return False
        
        # 保存數據
        crawler.save_to_json(tweets_data)
        crawler.save_to_csv(tweets_data) 
        
        # 生成分析
        analysis = crawler.analyze_trending_topics(tweets_data)
        crawler.save_to_json(analysis, "web3_analysis.json")
        
        total_tweets = sum(len(tweets) for tweets in tweets_data.values())
        logger.info(f"✅ 步驟1完成：成功爬取 {total_tweets} 條推文")
        success_count += 1
        
        # ===== 步驟2：生成新聞報告 =====
        logger.info("🤖 步驟2/3：使用OpenAI生成新聞報告...")
        
        reporter = Web3NewsReporter(
            openai_api_key=OPENAI_API_KEY,
            line_access_token=LINE_ACCESS_TOKEN, 
            line_user_id=LINE_USER_ID
        )
        
        # 生成報告（不自動發送）
        report = reporter.analyze_tweets_with_openai(tweets_data)
        
        if not report or "錯誤" in report:
            logger.error("❌ 新聞報告生成失敗")
            return False
        
        # 保存報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"web3_news_report_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ 步驟2完成：報告已保存到 {report_filename}")
        success_count += 1
        
        # ===== 步驟3：發送到LINE =====
        logger.info("📱 步驟3/3：發送到LINE...")
        
        line_success = reporter.send_to_line(report)
        
        if line_success:
            logger.info("✅ 步驟3完成：報告已發送到LINE")
            success_count += 1
        else:
            logger.error("❌ LINE發送失敗")
        
        # ===== 總結 =====
        logger.info("=" * 50)
        logger.info(f"📋 流程完成摘要：")
        logger.info(f"   成功步驟: {success_count}/{total_steps}")
        logger.info(f"   推文數量: {total_tweets}")
        logger.info(f"   報告文件: {report_filename}")
        logger.info(f"   LINE推播: {'✅ 成功' if line_success else '❌ 失敗'}")
        
        if success_count == total_steps:
            logger.info("🎉 每日Web3新聞流程執行成功！")
            return True
        else:
            logger.warning("⚠️  流程部分成功，請檢查日誌了解詳情")
            return False
            
    except Exception as e:
        logger.error(f"❌ 流程執行中發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    print("📰 每日Web3新聞自動化系統")
    print("=" * 50)
    print("功能：Twitter爬蟲 → OpenAI分析 → LINE推播")
    print("=" * 50)
    
    # 檢查是否為首次運行
    import os
    if not os.path.exists("news_reporter.py"):
        print("❌ 找不到必要文件，請確保所有腳本文件都在同一目錄")
        sys.exit(1)
    
    # 執行流程
    success = run_daily_pipeline()
    
    if success:
        print("\n🎊 恭喜！每日新聞流程執行成功")
        print("📱 請檢查你的LINE是否收到新聞報告")
    else:
        print("\n❌ 流程執行失敗")
        print("💡 建議：")
        print("   1. 檢查API參數是否正確設定")
        print("   2. 確認網路連接正常")
        print("   3. 查看日誌文件了解詳細錯誤")
        print("   4. 執行 python3 test_apis.py 測試API連接")

if __name__ == "__main__":
    main()