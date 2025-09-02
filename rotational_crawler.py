#!/usr/bin/env python3
"""
輪替式Web3爬蟲 - 解決多賽道問題的最終方案
每日只爬2-3個賽道，輪替進行，確保所有賽道都有覆蓋
"""

import tweepy
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入 LINE Bot 報告器
try:
    from news_reporter import Web3NewsReporter
    NEWS_REPORTER_AVAILABLE = True
except ImportError:
    NEWS_REPORTER_AVAILABLE = False

class RotationalWeb3Crawler:
    def __init__(self, bearer_token: str):
        """輪替式爬蟲 - 智能選擇今日要爬的賽道"""
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 7個賽道的輪替計劃
        self.web3_categories = {
            "DeFi": ["DeFi", "Uniswap", "compound"],
            "Layer1_Layer2": ["Ethereum", "Solana", "Polygon"], 
            "NFT_GameFi": ["NFT", "OpenSea", "gaming"],
            "AI_Crypto": ["AI", "ChatGPT", "artificial intelligence"],
            "RWA": ["RWA", "tokenization", "BlackRock"],
            "Meme_Coins": ["DOGE", "SHIB", "PEPE"],
            "Infrastructure": ["Chainlink", "oracle", "bridge"]
        }
        
        # 輪替狀態檔案
        self.rotation_file = "crawler_rotation_state.json"

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rotational_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_todays_categories(self) -> List[str]:
        """智能選擇今日要爬的賽道"""
        
        # 讀取輪替狀態
        if os.path.exists(self.rotation_file):
            try:
                with open(self.rotation_file, 'r') as f:
                    rotation_state = json.load(f)
            except:
                rotation_state = {"last_crawled": {}, "rotation_index": 0}
        else:
            rotation_state = {"last_crawled": {}, "rotation_index": 0}
        
        # 所有賽道
        all_categories = list(self.web3_categories.keys())
        
        # 今日日期
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 輪替邏輯：每日爬2個賽道，確保一週內覆蓋所有7個賽道
        start_index = rotation_state.get("rotation_index", 0)
        todays_categories = []
        
        # 選擇2個賽道
        for i in range(2):
            category_index = (start_index + i) % len(all_categories)
            todays_categories.append(all_categories[category_index])
        
        # 更新輪替狀態
        rotation_state["rotation_index"] = (start_index + 2) % len(all_categories)
        rotation_state["last_crawled"][today] = todays_categories
        
        # 保存狀態
        with open(self.rotation_file, 'w') as f:
            json.dump(rotation_state, f, indent=2)
        
        self.logger.info(f"📅 今日選定賽道: {', '.join(todays_categories)}")
        return todays_categories

    def crawl_single_category(self, category: str, keywords: List[str], max_results: int = 40) -> List[Dict[str, Any]]:
        """爬取單一賽道 - 使用最簡單策略"""
        
        tweets_data = []
        
        # 使用最簡單的關鍵字
        primary_keyword = keywords[0]
        query = f"{primary_keyword} -is:retweet lang:en"
        
        self.logger.info(f"🎯 爬取 {category}，查詢: {query}")
        
        try:
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                user_fields=['username', 'verified'],
                expansions=['author_id'],
                max_results=max_results
            )
            
            if not response or not response.data:
                self.logger.warning(f"⚠️ {category}: 無推文結果")
                return []
            
            # 處理用戶信息
            users = {}
            if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            # 處理推文
            for tweet in response.data:
                author = users.get(tweet.author_id)
                
                # 計算互動分數
                metrics = tweet.public_metrics or {}
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
            
            # 按互動度排序
            tweets_data.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            self.logger.info(f"✅ {category}: 成功獲得 {len(tweets_data)} 條推文")
            return tweets_data
            
        except tweepy.TooManyRequests as e:
            self.logger.error(f"❌ {category}: API限制，今日無法爬取此賽道")
            return []
        except Exception as e:
            self.logger.error(f"❌ {category}: 錯誤 - {str(e)}")
            return []

    def run_daily_crawl(self) -> Dict[str, List[Dict[str, Any]]]:
        """執行每日輪替爬取"""
        
        self.logger.info("🚀 開始輪替式Web3爬取...")
        
        # 選擇今日賽道
        todays_categories = self.get_todays_categories()
        
        all_tweets = {}
        total_crawled = 0
        
        for i, category in enumerate(todays_categories):
            self.logger.info(f"📊 處理 {category} ({i+1}/{len(todays_categories)})...")
            
            keywords = self.web3_categories[category]
            tweets = self.crawl_single_category(category, keywords, max_results=50)
            
            all_tweets[category] = tweets
            total_crawled += len(tweets)
            
            # 類別間延遲 - 如果不是最後一個
            if i < len(todays_categories) - 1 and tweets:  # 只有成功才延遲
                delay_minutes = 5  # 5分鐘延遲
                self.logger.info(f"⏰ 成功爬取，等待 {delay_minutes} 分鐘後處理下一個賽道...")
                time.sleep(delay_minutes * 60)
        
        # 為未爬取的賽道填入空陣列（保持結構完整）
        for category in self.web3_categories.keys():
            if category not in all_tweets:
                all_tweets[category] = []
        
        self.logger.info(f"🎉 今日輪替爬取完成！")
        self.logger.info(f"📈 爬取賽道: {', '.join([k for k, v in all_tweets.items() if v])}")
        self.logger.info(f"📊 總推文數: {total_crawled}")
        
        return all_tweets

    def save_results(self, data: Dict[str, List[Dict[str, Any]]]):
        """保存結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_filename = f"rotational_web3_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV
        all_tweets = []
        for category, tweets in data.items():
            all_tweets.extend(tweets)
        
        if all_tweets:
            all_tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
            csv_filename = f"rotational_web3_{timestamp}.csv"
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_tweets[0].keys())
                writer.writeheader()
                writer.writerows(all_tweets)
        
        self.logger.info(f"💾 結果已保存: {json_filename}")

def main():
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq")
    
    print("🔄 輪替式Web3爬蟲")
    print("=" * 50)
    print("🎯 策略: 每日爬2個賽道，一週覆蓋所有賽道")
    print("⚡ 優勢: 避免API限制，確保成功率")
    print("=" * 50)
    
    crawler = RotationalWeb3Crawler(BEARER_TOKEN)
    
    # 執行爬取
    results = crawler.run_daily_crawl()
    
    # 保存結果
    crawler.save_results(results)
    
    # 顯示結果摘要
    print("\n📊 今日爬取摘要:")
    successful_categories = 0
    total_tweets = 0
    
    for category, tweets in results.items():
        if tweets:
            successful_categories += 1
            total_tweets += len(tweets)
            avg_engagement = sum(t.get('engagement_score', 0) for t in tweets) / len(tweets)
            print(f"   ✅ {category}: {len(tweets)} 條推文 (平均互動: {avg_engagement:.1f})")
    
    print(f"\n🎉 成功爬取 {successful_categories} 個賽道，共 {total_tweets} 條推文")
    
    # LINE Bot 推播功能
    if successful_categories >= 1 and NEWS_REPORTER_AVAILABLE:
        try:
            print("\n📱 開始生成並推播 LINE 新聞報告...")
            
            # 獲取環境變數
            openai_key = os.getenv('OPENAI_API_KEY')
            line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
            line_user_id = os.getenv('LINE_USER_ID')
            
            if openai_key and line_token and line_user_id:
                # 初始化新聞報告器
                reporter = Web3NewsReporter(
                    openai_api_key=openai_key,
                    line_access_token=line_token,
                    line_user_id=line_user_id
                )
                
                # 生成並發送報告
                success = reporter.generate_and_send_report(results)
                if success:
                    print("✅ LINE 新聞報告已成功推播！")
                else:
                    print("❌ LINE 新聞報告推播失敗")
            else:
                print("⚠️ 缺少 API 設定，跳過 LINE 推播")
                
        except Exception as e:
            print(f"❌ LINE 推播過程發生錯誤: {str(e)}")
    
    if successful_categories >= 1:
        print("✅ 輪替策略成功！建議每日執行以實現完整覆蓋")
    else:
        print("❌ 今日爬取失敗，可能需要等待更長時間")

if __name__ == "__main__":
    main()