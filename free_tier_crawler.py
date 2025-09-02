#!/usr/bin/env python3
"""
Free Tier 專用爬蟲 - 每日1個賽道，7天完整輪替
適應 1次請求/15分鐘 的嚴格限制
"""

import tweepy
import json
import csv
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import os

class FreeTierWeb3Crawler:
    def __init__(self, bearer_token: str):
        """Free Tier專用 - 每日單賽道爬蟲"""
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 7個Web3賽道輪替順序
        self.web3_rotation = [
            ("DeFi", "DeFi"),
            ("Layer1_Layer2", "Ethereum"), 
            ("NFT_GameFi", "NFT"),
            ("AI_Crypto", "AI"),
            ("RWA", "RWA"),
            ("Meme_Coins", "DOGE"),
            ("Infrastructure", "Chainlink")
        ]
        
        # 狀態文件
        self.state_file = "free_tier_rotation_state.json"

    def setup_logging(self):
        """設置日誌"""
        timestamp = datetime.now().strftime("%Y%m%d")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'free_tier_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_today_category(self) -> tuple:
        """獲取今日要爬的賽道"""
        
        # 讀取輪替狀態
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
            except:
                state = {"rotation_index": 0, "last_crawl_date": None}
        else:
            state = {"rotation_index": 0, "last_crawl_date": None}
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 如果今天已經爬過，返回今天的賽道
        if state.get("last_crawl_date") == today:
            current_index = state["rotation_index"]
            category, keyword = self.web3_rotation[current_index]
            self.logger.info(f"📅 今日已爬取: {category}")
            return category, keyword, False  # False表示今天已爬過
        
        # 選擇今日賽道
        current_index = state["rotation_index"]
        category, keyword = self.web3_rotation[current_index]
        
        # 更新狀態
        next_index = (current_index + 1) % len(self.web3_rotation)
        state.update({
            "rotation_index": next_index,
            "last_crawl_date": today,
            "today_category": category
        })
        
        # 保存狀態
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"📅 今日選定賽道: {category} (關鍵字: {keyword})")
        self.logger.info(f"🔄 明日將爬取: {self.web3_rotation[next_index][0]}")
        
        return category, keyword, True  # True表示需要爬取

    def crawl_single_category_free_tier(self, category: str, keyword: str) -> List[Dict[str, Any]]:
        """Free Tier安全爬取 - 只用1次API請求"""
        
        self.logger.info(f"🎯 Free Tier爬取: {category}")
        self.logger.info("⚠️ 使用1次API請求，獲取最大數量推文")
        
        try:
            query = f"{keyword} -is:retweet lang:en"
            self.logger.info(f"   查詢: {query}")
            
            # 使用最大max_results=100來充分利用這1次請求
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                user_fields=['username', 'verified', 'public_metrics'],
                expansions=['author_id'],
                max_results=100  # Free tier要充分利用每次請求
            )
            
            if not response or not response.data:
                self.logger.warning(f"⚠️ {category}: 無推文結果")
                return []
            
            # 處理用戶信息
            users = {}
            if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            tweets_data = []
            
            # 處理推文
            for tweet in response.data:
                author = users.get(tweet.author_id)
                metrics = tweet.public_metrics or {}
                
                # 計算互動分數
                engagement_score = (
                    metrics.get('like_count', 0) * 1 +
                    metrics.get('retweet_count', 0) * 2 +
                    metrics.get('reply_count', 0) * 0.5
                )
                
                tweet_data = {
                    'category': category,
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
                    'username': getattr(author, 'username', 'unknown') if author else 'unknown',
                    'verified': getattr(author, 'verified', False) if author else False,
                    'retweet_count': metrics.get('retweet_count', 0),
                    'like_count': metrics.get('like_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0),
                    'engagement_score': engagement_score,
                    'url': f"https://twitter.com/{getattr(author, 'username', 'unknown') if author else 'unknown'}/status/{tweet.id}"
                }
                tweets_data.append(tweet_data)
            
            # 按互動度排序，取前30條精選
            tweets_data.sort(key=lambda x: x['engagement_score'], reverse=True)
            tweets_data = tweets_data[:30]  # 精選30條
            
            self.logger.info(f"✅ {category}: 成功獲得 {len(tweets_data)} 條精選推文")
            return tweets_data
            
        except tweepy.TooManyRequests:
            self.logger.error(f"❌ {category}: API限制 - Free tier每15分鐘只能1次請求")
            return []
        except Exception as e:
            self.logger.error(f"❌ {category}: 錯誤 - {str(e)}")
            return []

    def run_daily_free_tier_crawl(self) -> Dict[str, List[Dict[str, Any]]]:
        """執行Free Tier每日爬取"""
        
        self.logger.info("🆓 Free Tier每日Web3爬取")
        self.logger.info("🎯 策略: 每日1個賽道，7天完整輪替")
        
        # 獲取今日賽道
        category, keyword, need_crawl = self.get_today_category()
        
        if not need_crawl:
            self.logger.info("✅ 今日已完成爬取")
            # 嘗試載入今日結果
            try:
                today = datetime.now().strftime("%Y%m%d")
                json_files = [f for f in os.listdir('.') if f.startswith(f'free_tier_{today}') and f.endswith('.json')]
                if json_files:
                    latest_file = sorted(json_files)[-1]
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except:
                pass
            return {category: []}
        
        # 執行爬取
        tweets = self.crawl_single_category_free_tier(category, keyword)
        
        # 構建結果 - 為保持結構一致性，包含所有賽道
        all_tweets = {}
        for cat_name, _ in self.web3_rotation:
            all_tweets[cat_name] = tweets if cat_name == category else []
        
        self.logger.info(f"🎉 今日Free Tier爬取完成")
        self.logger.info(f"📊 {category}: {len(tweets)} 條推文")
        
        return all_tweets

    def save_results(self, data: Dict[str, List[Dict[str, Any]]], category: str):
        """保存結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 保存
        json_filename = f"free_tier_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV 保存 (只保存今日爬取的賽道)
        today_tweets = data.get(category, [])
        if today_tweets:
            csv_filename = f"free_tier_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=today_tweets[0].keys())
                writer.writeheader()
                writer.writerows(today_tweets)
        
        self.logger.info(f"💾 結果已保存: {json_filename}")
        return json_filename

def main():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🆓 Free Tier Web3爬蟲")
    print("=" * 50)
    print("📋 適應策略: 每日1個賽道，7天完整覆蓋")
    print("⚡ API限制: 1次請求/15分鐘")
    print("🎯 每次獲取: 30條精選推文")
    print("=" * 50)
    
    crawler = FreeTierWeb3Crawler(BEARER_TOKEN)
    
    # 執行爬取
    results = crawler.run_daily_free_tier_crawl()
    
    # 找出今日爬取的賽道
    today_category = None
    today_count = 0
    for category, tweets in results.items():
        if tweets:
            today_category = category
            today_count = len(tweets)
            break
    
    if today_category:
        # 保存結果
        filename = crawler.save_results(results, today_category)
        
        # 顯示結果摘要
        print(f"\n📊 Free Tier每日爬取結果:")
        print(f"   🎯 今日賽道: {today_category}")
        print(f"   📈 推文數量: {today_count}")
        
        if today_count > 0:
            avg_engagement = sum(t.get('engagement_score', 0) for t in results[today_category]) / today_count
            print(f"   💫 平均互動度: {avg_engagement:.1f}")
        
        print(f"\n✅ Free Tier策略運行成功！")
        print(f"📅 明日將自動輪替到下一個賽道")
        print(f"🔄 7天後完整覆蓋所有Web3賽道")
        
    else:
        print("⚠️ 今日已完成爬取或遇到問題")

if __name__ == "__main__":
    main()