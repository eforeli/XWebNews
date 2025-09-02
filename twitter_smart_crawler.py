#!/usr/bin/env python3
"""
智能Web3 Twitter爬蟲 - 優化版本
針對API限制進行優化，支持分批執行和智能重試
"""

import tweepy
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import random

class SmartWeb3Crawler:
    def __init__(self, bearer_token: str):
        """
        初始化智能Web3 Twitter爬蟲
        
        Args:
            bearer_token: Twitter API Bearer Token
        """
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 每日分配策略：7個類別 × 每類別20條 = 140條推文/天
        # 確保在10,000條/月限制內 (140 × 30 = 4,200條/月)
        self.daily_tweet_limit = 140
        self.tweets_per_category = 20
        
        # Web3賽道關鍵字 - 優化版（更精準）
        self.web3_categories = {
            "DeFi": {
                "keywords": ["DeFi", "UniSwap", "SushiSwap", "Compound", "Aave", "Curve", "PancakeSwap"],
                "priority": 1  # 最高優先級
            },
            "Layer1_Layer2": {
                "keywords": ["Ethereum", "Solana", "Polygon", "Arbitrum", "Optimism", "Base", "zkSync"],
                "priority": 2
            },
            "NFT_GameFi": {
                "keywords": ["NFT", "OpenSea", "GameFi", "play to earn", "P2E", "Axie", "metaverse"],
                "priority": 3
            },
            "AI_Crypto": {
                "keywords": ["AI crypto", "ChatGPT", "artificial intelligence", "FET", "AGIX", "OCEAN"],
                "priority": 2
            },
            "RWA": {
                "keywords": ["RWA", "real world assets", "tokenization", "BlackRock", "asset backed"],
                "priority": 3
            },
            "Meme_Coins": {
                "keywords": ["DOGE", "SHIB", "PEPE", "meme coin", "Dogecoin", "Shiba Inu"],
                "priority": 4  # 最低優先級
            },
            "Infrastructure": {
                "keywords": ["Chainlink", "oracle", "cross-chain", "bridge", "LINK", "interoperability"],
                "priority": 2
            }
        }

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('smart_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_rate_limit_status(self):
        """檢查API使用狀況"""
        try:
            # 注意：這個調用本身也會消耗API配額
            limits = self.client.get_rate_limit_status()
            return limits
        except Exception as e:
            self.logger.warning(f"無法獲取速率限制狀況: {str(e)}")
            return None

    def smart_search_tweets(self, category: str, config: Dict, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        智能搜尋推文 - 加入重試邏輯和錯誤處理
        
        Args:
            category: Web3類別名稱
            config: 類別配置（關鍵字和優先級）
            max_results: 最大結果數量
            
        Returns:
            推文數據列表
        """
        tweets_data = []
        keywords = config["keywords"]
        
        # 構建更精準的查詢字符串
        # 使用高價值關鍵字，過濾低質量內容
        primary_keywords = keywords[:3]  # 使用前3個最重要的關鍵字
        query = " OR ".join([f'"{keyword}"' for keyword in primary_keywords])
        
        # 添加過濾條件
        query += " -is:retweet -is:reply lang:en"  # 排除轉推和回復，只要英文
        query += " has:links"  # 只要包含連結的推文（通常質量較高）
        
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"正在搜尋 {category} 類別... (嘗試 {attempt + 1}/{max_retries})")
                self.logger.debug(f"查詢字符串: {query}")
                
                # 直接調用search_recent_tweets，避免Paginator的複雜性
                response = self.client.search_recent_tweets(
                    query=query,
                    tweet_fields=['created_at', 'author_id', 'public_metrics'],
                    user_fields=['username', 'verified'],
                    expansions=['author_id'],
                    max_results=min(max_results, 100)
                )
                
                tweets = response.data if response.data else []
                
                users = {}
                # 處理用戶數據
                if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                    users = {user.id: user for user in response.includes['users']}
                
                for tweet in tweets:
                    # 獲取用戶信息
                    author = users.get(tweet.author_id)
                    
                    # 計算質量分數（用於排序）
                    quality_score = (
                        tweet.public_metrics['like_count'] * 2 +
                        tweet.public_metrics['retweet_count'] * 3 +
                        tweet.public_metrics['reply_count'] * 1
                    )
                    
                    tweet_data = {
                        'category': category,
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'author_id': tweet.author_id,
                        'username': getattr(author, 'username', 'unknown') if author else 'unknown',
                        'verified': getattr(author, 'verified', False) if author else False,
                        'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                        'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                        'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0,
                        'quote_count': tweet.public_metrics['quote_count'] if tweet.public_metrics else 0,
                        'quality_score': quality_score,
                        'url': f"https://twitter.com/{getattr(author, 'username', 'unknown') if author else 'unknown'}/status/{tweet.id}"
                    }
                    tweets_data.append(tweet_data)
                
                # 按質量分數排序，取最好的
                tweets_data.sort(key=lambda x: x['quality_score'], reverse=True)
                tweets_data = tweets_data[:max_results]
                
                self.logger.info(f"✅ {category} 類別找到 {len(tweets_data)} 條高質量推文")
                return tweets_data
                
            except tweepy.TooManyRequests:
                wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                self.logger.warning(f"❌ API限制 - {category}，等待 {wait_time:.1f} 秒後重試...")
                time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"搜尋 {category} 時發生錯誤: {str(e)}")
                if attempt == max_retries - 1:
                    break
                time.sleep(base_delay)
        
        return tweets_data

    def crawl_by_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        按優先級爬取數據 - 確保重要類別優先獲得數據
        
        Returns:
            按類別分組的推文數據
        """
        self.logger.info("🎯 開始智能優先級爬取...")
        
        # 按優先級排序類別
        sorted_categories = sorted(
            self.web3_categories.items(),
            key=lambda x: x[1]["priority"]
        )
        
        all_tweets = {}
        total_crawled = 0
        
        for category, config in sorted_categories:
            if total_crawled >= self.daily_tweet_limit:
                self.logger.info(f"⚠️  達到每日限制 ({self.daily_tweet_limit} 條)，停止爬取")
                break
            
            remaining_quota = self.daily_tweet_limit - total_crawled
            tweets_for_this_category = min(self.tweets_per_category, remaining_quota)
            
            self.logger.info(f"📊 爬取 {category} (優先級 {config['priority']})，目標 {tweets_for_this_category} 條")
            
            tweets = self.smart_search_tweets(category, config, tweets_for_this_category)
            all_tweets[category] = tweets
            
            if tweets:
                total_crawled += len(tweets)
                self.logger.info(f"✅ 成功獲得 {len(tweets)} 條，總計 {total_crawled}/{self.daily_tweet_limit}")
            
            # 智能延遲：根據剩餘類別調整等待時間
            remaining_categories = len(sorted_categories) - len(all_tweets)
            if remaining_categories > 0:
                delay_time = max(3, 15 / remaining_categories)  # 平均分配等待時間
                self.logger.info(f"⏰ 等待 {delay_time:.1f} 秒後繼續...")
                time.sleep(delay_time)
        
        self.logger.info(f"🎉 智能爬取完成！總共獲得 {total_crawled} 條推文")
        return all_tweets

    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """保存數據為JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smart_web3_tweets_{timestamp}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"💾 數據已保存到 {filename}")
        except Exception as e:
            self.logger.error(f"保存JSON文件時發生錯誤: {str(e)}")

    def save_to_csv(self, data: Dict[str, List[Dict[str, Any]]], filename: str = None):
        """保存數據為CSV文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smart_web3_tweets_{timestamp}.csv"
            
        try:
            # 展平所有推文數據
            all_tweets = []
            for category, tweets in data.items():
                all_tweets.extend(tweets)
                
            if all_tweets:
                # 按質量分數排序
                all_tweets.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                
                fieldnames = all_tweets[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_tweets)
                    
                self.logger.info(f"💾 數據已保存到 {filename}")
            else:
                self.logger.warning("沒有數據可保存")
                
        except Exception as e:
            self.logger.error(f"保存CSV文件時發生錯誤: {str(e)}")

def main():
    # Twitter API Bearer Token
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🚀 智能Web3 Twitter爬蟲 v2.0")
    print("="*50)
    print("🎯 特色：優先級爬取 + 智能重試 + 質量過濾")
    print("="*50)
    
    # 創建智能爬蟲實例
    crawler = SmartWeb3Crawler(BEARER_TOKEN)
    
    # 執行智能爬取
    all_tweets = crawler.crawl_by_priority()
    
    # 保存數據
    crawler.save_to_json(all_tweets)
    crawler.save_to_csv(all_tweets)
    
    # 顯示統計
    print("\n📊 爬取結果統計：")
    total_tweets = 0
    for category, tweets in all_tweets.items():
        if tweets:
            print(f"   {category}: {len(tweets)} 條推文")
            total_tweets += len(tweets)
    
    print(f"\n🎉 總共成功爬取 {total_tweets} 條高質量Web3推文")
    print("💡 提示：數據已按質量分數排序，優先顯示高互動度內容")

if __name__ == "__main__":
    main()