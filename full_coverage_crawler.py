#!/usr/bin/env python3
"""
每日全覆蓋爬蟲 - 每天爬取所有7個Web3賽道
使用分時段策略避開API限制
"""

import tweepy
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import random
import os

class FullCoverageWeb3Crawler:
    def __init__(self, bearer_token: str):
        """每日全覆蓋爬蟲 - 智能分時段爬取所有賽道"""
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 7個Web3賽道 - 每個賽道精選關鍵字
        self.web3_categories = {
            "DeFi": "DeFi",
            "Layer1_Layer2": "Ethereum", 
            "NFT_GameFi": "NFT",
            "AI_Crypto": "AI",
            "RWA": "RWA",
            "Meme_Coins": "DOGE",
            "Infrastructure": "Chainlink"
        }

    def setup_logging(self):
        """設置日誌"""
        timestamp = datetime.now().strftime("%Y%m%d")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'full_coverage_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def crawl_single_category_safe(self, category: str, keyword: str, target_tweets: int = 15) -> List[Dict[str, Any]]:
        """安全爬取單一賽道 - 包含錯誤處理和重試"""
        
        tweets_data = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🎯 爬取 {category} (嘗試 {attempt + 1}/{max_retries})")
                
                query = f"{keyword} -is:retweet lang:en"
                
                response = self.client.search_recent_tweets(
                    query=query,
                    tweet_fields=['created_at', 'author_id', 'public_metrics'],
                    user_fields=['username', 'verified'],
                    expansions=['author_id'],
                    max_results=min(target_tweets + 5, 100)  # 多抓一些以備篩選
                )
                
                if not response or not response.data:
                    self.logger.warning(f"   ⚠️ {category}: 無推文結果")
                    if attempt < max_retries - 1:
                        time.sleep(30)  # 等待30秒後重試
                        continue
                    return []
                
                # 處理用戶信息
                users = {}
                if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                    users = {user.id: user for user in response.includes['users']}
                
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
                
                # 按互動度排序，取最好的
                tweets_data.sort(key=lambda x: x['engagement_score'], reverse=True)
                tweets_data = tweets_data[:target_tweets]
                
                self.logger.info(f"   ✅ {category}: 成功獲得 {len(tweets_data)} 條推文")
                return tweets_data
                
            except tweepy.TooManyRequests:
                self.logger.warning(f"   ⚠️ {category}: API限制 (嘗試 {attempt + 1})")
                if attempt < max_retries - 1:
                    # 指數退避：30秒、2分鐘、5分鐘
                    wait_time = [30, 120, 300][attempt]
                    self.logger.info(f"   ⏰ 等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"   ❌ {category}: 達到重試上限，跳過此賽道")
                    return []
                    
            except Exception as e:
                self.logger.error(f"   ❌ {category}: 錯誤 - {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                else:
                    return []
        
        return tweets_data

    def crawl_all_categories_distributed(self) -> Dict[str, List[Dict[str, Any]]]:
        """分時段爬取所有賽道 - 每日全覆蓋"""
        
        self.logger.info("🚀 開始每日全覆蓋Web3爬取...")
        self.logger.info("🎯 目標: 涵蓋所有7個Web3賽道")
        
        all_tweets = {}
        total_crawled = 0
        successful_categories = 0
        
        categories_list = list(self.web3_categories.items())
        random.shuffle(categories_list)  # 隨機順序避免模式
        
        for i, (category, keyword) in enumerate(categories_list):
            self.logger.info(f"📊 處理 {category} ({i+1}/{len(categories_list)})...")
            
            # 爬取這個賽道
            tweets = self.crawl_single_category_safe(category, keyword, target_tweets=15)
            all_tweets[category] = tweets
            
            if tweets:
                total_crawled += len(tweets)
                successful_categories += 1
                self.logger.info(f"✅ {category}: {len(tweets)} 條推文，累計 {total_crawled}")
            else:
                self.logger.warning(f"⚠️ {category}: 未獲得推文")
            
            # 類別間智能延遲
            if i < len(categories_list) - 1:  # 不是最後一個
                # 基於成功率調整延遲
                if tweets:  # 成功了
                    delay = random.uniform(90, 150)  # 1.5-2.5分鐘
                else:  # 失敗了
                    delay = random.uniform(180, 300)  # 3-5分鐘
                
                self.logger.info(f"⏰ 等待 {delay:.0f} 秒後處理下一賽道...")
                time.sleep(delay)
        
        # 結果統計
        self.logger.info("🎉 每日全覆蓋爬取完成！")
        self.logger.info(f"📈 成功賽道: {successful_categories}/{len(categories_list)}")
        self.logger.info(f"📊 總推文數: {total_crawled}")
        
        # 顯示各賽道結果
        for category, tweets in all_tweets.items():
            if tweets:
                avg_engagement = sum(t['engagement_score'] for t in tweets) / len(tweets)
                self.logger.info(f"   ✅ {category}: {len(tweets)}條，平均熱度 {avg_engagement:.1f}")
            else:
                self.logger.info(f"   ❌ {category}: 0條")
        
        return all_tweets

    def save_results(self, data: Dict[str, List[Dict[str, Any]]]):
        """保存結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 保存
        json_filename = f"full_coverage_web3_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV 保存 (所有推文合併)
        all_tweets = []
        for category, tweets in data.items():
            all_tweets.extend(tweets)
        
        if all_tweets:
            # 按熱度排序
            all_tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
            
            csv_filename = f"full_coverage_web3_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_tweets[0].keys())
                writer.writeheader()
                writer.writerows(all_tweets)
            
            self.logger.info(f"💾 結果已保存: {json_filename} & {csv_filename}")
        
        return json_filename

def main():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🌍 每日全覆蓋Web3爬蟲")
    print("=" * 50)
    print("🎯 策略: 每日涵蓋所有7個Web3賽道")
    print("⚡ 方法: 分時段 + 智能重試 + 指數退避")
    print("📊 目標: 每賽道15條精選推文")
    print("=" * 50)
    
    crawler = FullCoverageWeb3Crawler(BEARER_TOKEN)
    
    # 執行爬取
    results = crawler.crawl_all_categories_distributed()
    
    # 保存結果
    filename = crawler.save_results(results)
    
    # 顯示最終統計
    print("\n📊 每日全覆蓋結果摘要:")
    successful_categories = 0
    total_tweets = 0
    
    for category, tweets in results.items():
        if tweets:
            successful_categories += 1
            total_tweets += len(tweets)
            avg_engagement = sum(t.get('engagement_score', 0) for t in tweets) / len(tweets)
            print(f"   ✅ {category}: {len(tweets)} 條推文 (熱度: {avg_engagement:.1f})")
        else:
            print(f"   ❌ {category}: 無推文")
    
    coverage_rate = (successful_categories / 7) * 100
    print(f"\n🎉 覆蓋率: {coverage_rate:.1f}% ({successful_categories}/7 賽道)")
    print(f"📈 總推文: {total_tweets} 條")
    
    if coverage_rate >= 80:
        print("✅ 優秀！幾乎完整覆蓋所有Web3賽道")
    elif coverage_rate >= 60:
        print("✅ 良好！覆蓋大部分Web3賽道")
    else:
        print("⚠️ 部分成功，可能需要調整API使用策略")

if __name__ == "__main__":
    main()