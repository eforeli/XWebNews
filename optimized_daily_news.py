#!/usr/bin/env python3
"""
優化版每日Web3新聞 - 基於已驗證的爬蟲，加入智能策略
"""

import sys
import os
import logging
import time
from datetime import datetime
from twitter_web3_crawler import TwitterWeb3Crawler
from news_reporter import Web3NewsReporter
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def setup_logging():
    """設置日誌"""
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = f"optimized_news_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_optimized_pipeline():
    """執行優化版每日新聞流程"""
    
    logger = setup_logging()
    logger.info("🚀 開始執行優化版Web3新聞流程...")
    
    # Twitter API設定
    TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    # OpenAI和LINE設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'your_line_channel_access_token_here')
    LINE_USER_ID = os.getenv('LINE_USER_ID', 'your_line_user_id_here')
    
    success_count = 0
    total_steps = 3
    
    try:
        # ===== 步驟1：優化版Twitter爬取 =====
        logger.info("📊 步驟1/3：優化版Twitter精選爬取...")
        
        crawler = TwitterWeb3Crawler(TWITTER_BEARER_TOKEN)
        
        # 優先級類別配置（基於重要性）
        priority_categories = [
            ("DeFi", 30),           # 最重要，多抓一些
            ("Layer1_Layer2", 25),  # 重要
            ("NFT_GameFi", 20),     # 中等重要
            ("AI_Crypto", 15),      # 興趣類別
            ("Infrastructure", 15), # 基礎設施
            ("RWA", 10),           # 新興領域
            ("Meme_Coins", 5)      # 娛樂類別，最少
        ]
        
        all_tweets = {}
        total_crawled = 0
        max_daily_tweets = 140  # 每日精選限制
        
        for category, target_count in priority_categories:
            if total_crawled >= max_daily_tweets:
                logger.info(f"⚠️ 達到每日精選限制 ({max_daily_tweets} 條)，停止爬取")
                break
            
            logger.info(f"🎯 爬取 {category} 類別，目標 {target_count} 條精選推文")
            
            # 使用原始爬蟲方法，但調整參數
            try:
                category_tweets = crawler.search_tweets_by_category(
                    category, 
                    crawler.web3_categories[category],
                    max_results=target_count
                )
                
                if category_tweets:
                    # 按互動度排序，取最好的
                    category_tweets.sort(
                        key=lambda x: x.get('like_count', 0) + x.get('retweet_count', 0) * 2, 
                        reverse=True
                    )
                    
                    # 限制在目標數量內
                    category_tweets = category_tweets[:target_count]
                    all_tweets[category] = category_tweets
                    total_crawled += len(category_tweets)
                    
                    logger.info(f"✅ {category}: 成功獲得 {len(category_tweets)} 條，累計 {total_crawled}")
                else:
                    logger.warning(f"⚠️ {category}: 未獲得任何推文")
                    all_tweets[category] = []
                
            except Exception as e:
                logger.warning(f"⚠️ {category} 爬取失敗: {str(e)}")
                all_tweets[category] = []
            
            # 智能延遲：避免API限制
            if category != priority_categories[-1][0]:  # 不是最後一個類別
                logger.info("⏰ 等待10秒避免API限制...")
                time.sleep(10)
        
        if total_crawled == 0:
            # 如果完全失敗，嘗試加載之前的數據
            logger.warning("⚠️ 本次爬取失敗，嘗試使用之前的數據...")
            import glob
            import os
            import json
            
            json_files = glob.glob("*web3_tweets*.json")
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                logger.info(f"使用數據文件: {latest_file}")
                with open(latest_file, 'r', encoding='utf-8') as f:
                    all_tweets = json.load(f)
                total_crawled = sum(len(tweets) for tweets in all_tweets.values())
            else:
                logger.error("❌ 沒有任何可用數據")
                return False
        
        # 保存數據
        crawler.save_to_json(all_tweets)
        crawler.save_to_csv(all_tweets)
        
        logger.info(f"✅ 步驟1完成：成功獲得 {total_crawled} 條精選推文")
        success_count += 1
        
        # ===== 步驟2：AI新聞分析 =====
        logger.info("🤖 步驟2/3：AI智能新聞分析...")
        
        reporter = Web3NewsReporter(
            openai_api_key=OPENAI_API_KEY,
            line_access_token=LINE_ACCESS_TOKEN, 
            line_user_id=LINE_USER_ID
        )
        
        # 生成優化版提示，強調精選內容
        report = reporter.analyze_tweets_with_openai(all_tweets)
        
        if not report or "錯誤" in report:
            logger.error("❌ AI新聞分析失敗")
            return False
        
        # 保存報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"optimized_news_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(f"📊 基於 {total_crawled} 條精選推文生成\n")
            f.write("="*50 + "\n\n")
            f.write(report)
        
        logger.info(f"✅ 步驟2完成：報告已保存到 {report_filename}")
        success_count += 1
        
        # ===== 步驟3：LINE推播 =====
        logger.info("📱 步驟3/3：發送精選新聞到LINE...")
        
        # 在報告前加入統計信息
        enhanced_report = f"📊 今日Web3精選 ({total_crawled}條推文)\n" + "="*30 + "\n\n" + report
        
        line_success = reporter.send_to_line(enhanced_report)
        
        if line_success:
            logger.info("✅ 步驟3完成：精選新聞已推送到LINE")
            success_count += 1
        else:
            logger.error("❌ LINE推送失敗")
        
        # ===== 總結 =====
        logger.info("=" * 50)
        logger.info(f"📋 優化流程完成摘要：")
        logger.info(f"   成功步驟: {success_count}/{total_steps}")
        logger.info(f"   精選推文: {total_crawled} 條")
        logger.info(f"   報告文件: {report_filename}")
        logger.info(f"   LINE推播: {'✅ 成功' if line_success else '❌ 失敗'}")
        
        if success_count == total_steps:
            logger.info("🎉 優化版Web3新聞流程執行成功！")
            return True
        else:
            logger.warning("⚠️ 流程部分成功，請檢查日誌")
            return False
            
    except Exception as e:
        logger.error(f"❌ 流程執行錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    print("📰 優化版Web3新聞系統")
    print("=" * 50)
    print("🎯 特色：140條每日精選 + 優先級爬取 + 智能分析")
    print("=" * 50)
    
    # 執行優化流程
    success = run_optimized_pipeline()
    
    if success:
        print("\n🎊 恭喜！優化版新聞流程執行成功")
        print("📱 請檢查LINE接收精選Web3新聞報告")
        print("💡 報告基於高互動度精選推文生成，質量更高")
    else:
        print("\n❌ 流程執行失敗")
        print("💡 建議檢查日誌文件了解詳情")

if __name__ == "__main__":
    main()