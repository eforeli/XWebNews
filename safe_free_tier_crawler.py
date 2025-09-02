#!/usr/bin/env python3
"""
保守Free Tier爬蟲 - 確保完全符合所有API限制
- Rate Limit: 1次請求/15分鐘  
- 月度限制: 100 Posts/月 (保守解讀為獲取的推文數)
- 每次請求: 10條推文 (確保月度額度可用10次)
"""

import tweepy
import json
import csv
from datetime import datetime
from typing import List, Dict, Any
import logging
import os

class SafeFreeTierCrawler:
    def __init__(self, bearer_token: str):
        """超保守Free Tier爬蟲 - 確保不違反任何限制"""
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 保守設定
        self.monthly_post_limit = 100  # Free tier月度限制
        self.posts_per_request = 10    # 每次只獲取10條，確保可用10次
        self.usage_tracking_file = "free_tier_usage.json"
        
        # 輪替賽道策略
        self.web3_rotation = [
            ("DeFi", "DeFi"),
            ("Layer1_Layer2", "Ethereum"), 
            ("NFT_GameFi", "NFT"),
            ("AI_Crypto", "AI"),
            ("RWA", "RWA"),
            ("Meme_Coins", "DOGE"),
            ("Infrastructure", "Chainlink")
        ]

    def setup_logging(self):
        """設置日誌"""
        timestamp = datetime.now().strftime("%Y%m%d")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'safe_free_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_monthly_usage(self) -> dict:
        """檢查月度使用量"""
        current_month = datetime.now().strftime("%Y-%m")
        
        if os.path.exists(self.usage_tracking_file):
            try:
                with open(self.usage_tracking_file, 'r') as f:
                    usage_data = json.load(f)
            except:
                usage_data = {}
        else:
            usage_data = {}
        
        # 初始化當月數據
        if current_month not in usage_data:
            usage_data[current_month] = {
                "requests_made": 0,
                "posts_retrieved": 0,
                "last_request_date": None
            }
        
        return usage_data

    def update_usage(self, posts_count: int):
        """更新使用量記錄"""
        current_month = datetime.now().strftime("%Y-%m")
        today = datetime.now().strftime("%Y-%m-%d")
        
        usage_data = self.check_monthly_usage()
        usage_data[current_month]["requests_made"] += 1
        usage_data[current_month]["posts_retrieved"] += posts_count
        usage_data[current_month]["last_request_date"] = today
        
        with open(self.usage_tracking_file, 'w') as f:
            json.dump(usage_data, f, indent=2)

    def get_today_category(self) -> tuple:
        """獲取今日賽道（輪替策略）"""
        state_file = "rotation_state.json"
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
            except:
                state = {"rotation_index": 0, "last_date": None}
        else:
            state = {"rotation_index": 0, "last_date": None}
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 如果今天已爬過，返回今天的賽道
        if state.get("last_date") == today:
            current_index = state["rotation_index"]
            category, keyword = self.web3_rotation[current_index]
            return category, keyword, False  # 已爬過
        
        # 選擇今日賽道
        current_index = state["rotation_index"]
        category, keyword = self.web3_rotation[current_index]
        
        # 更新狀態
        next_index = (current_index + 1) % len(self.web3_rotation)
        state.update({
            "rotation_index": next_index,
            "last_date": today,
            "today_category": category
        })
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        return category, keyword, True  # 需要爬取

    def safe_crawl(self) -> Dict[str, List[Dict[str, Any]]]:
        """執行超保守爬取"""
        
        self.logger.info("🛡️ 超保守Free Tier爬蟲")
        self.logger.info("📊 月度限制: 100 Posts/月")
        self.logger.info("⚡ 每次獲取: 10條推文")
        self.logger.info("🎯 策略: 輪替賽道")
        
        # 檢查月度使用量
        usage_data = self.check_monthly_usage()
        current_month = datetime.now().strftime("%Y-%m")
        monthly_usage = usage_data[current_month]
        
        self.logger.info(f"📈 本月已使用: {monthly_usage['posts_retrieved']}/100 Posts")
        self.logger.info(f"📈 本月請求次數: {monthly_usage['requests_made']}")
        
        # 檢查是否還能使用
        if monthly_usage["posts_retrieved"] + self.posts_per_request > self.monthly_post_limit:
            self.logger.error(f"❌ 月度額度不足！還需 {self.posts_per_request} Posts，但只剩 {self.monthly_post_limit - monthly_usage['posts_retrieved']}")
            return {cat[0]: [] for cat in self.web3_rotation}
        
        # 獲取今日賽道
        category, keyword, need_crawl = self.get_today_category()
        
        if not need_crawl:
            self.logger.info(f"✅ 今日已完成 {category} 爬取")
            return {cat[0]: [] if cat[0] != category else [{"info": "today_already_crawled"}] for cat in self.web3_rotation}
        
        self.logger.info(f"🎯 今日賽道: {category} (關鍵字: {keyword})")
        
        try:
            # 超保守API請求
            query = f"{keyword} -is:retweet lang:en"
            
            response = self.client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                user_fields=['username', 'verified'],
                expansions=['author_id'],
                max_results=self.posts_per_request  # 只獲取10條
            )
            
            if not response or not response.data:
                self.logger.warning(f"⚠️ {category}: 無推文結果")
                # 仍然消耗了API配額，需要記錄
                self.update_usage(0)
                return {cat[0]: [] for cat in self.web3_rotation}
            
            # 處理用戶信息
            users = {}
            if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            tweets_data = []
            
            # 處理推文
            for tweet in response.data:
                author = users.get(tweet.author_id)
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
            
            # 更新使用量
            self.update_usage(len(tweets_data))
            
            self.logger.info(f"✅ {category}: 成功獲得 {len(tweets_data)} 條推文")
            self.logger.info(f"📊 本月剩餘額度: {self.monthly_post_limit - monthly_usage['posts_retrieved'] - len(tweets_data)} Posts")
            
            # 構建結果
            result = {cat[0]: [] for cat in self.web3_rotation}
            result[category] = tweets_data
            
            return result
            
        except tweepy.TooManyRequests:
            self.logger.error("❌ API限制 - 15分鐘內已達1次請求限制")
            return {cat[0]: [] for cat in self.web3_rotation}
        except Exception as e:
            self.logger.error(f"❌ 爬取錯誤: {str(e)}")
            return {cat[0]: [] for cat in self.web3_rotation}

    def save_results(self, data: Dict[str, List[Dict[str, Any]]]):
        """保存結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 保存
        json_filename = f"safe_free_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV 保存 (只保存有數據的賽道)
        all_tweets = []
        for category, tweets in data.items():
            # 過濾掉標記項
            valid_tweets = [t for t in tweets if 'tweet_id' in t]
            all_tweets.extend(valid_tweets)
        
        if all_tweets:
            csv_filename = f"safe_free_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_tweets[0].keys())
                writer.writeheader()
                writer.writerows(all_tweets)
        
        self.logger.info(f"💾 結果已保存: {json_filename}")
        return json_filename

def main():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🛡️ 超保守Free Tier爬蟲")
    print("=" * 50)
    print("📊 月度限制: 100 Posts/月")
    print("⚡ Rate Limit: 1次請求/15分鐘")
    print("🎯 每次獲取: 10條推文")
    print("🔄 策略: 7天輪替賽道")
    print("=" * 50)
    
    crawler = SafeFreeTierCrawler(BEARER_TOKEN)
    
    # 執行保守爬取
    results = crawler.safe_crawl()
    
    # 保存結果
    filename = crawler.save_results(results)
    
    # 顯示結果摘要
    print(f"\n📊 保守爬取結果:")
    today_category = None
    today_count = 0
    
    for category, tweets in results.items():
        valid_tweets = [t for t in tweets if 'tweet_id' in t]
        if valid_tweets:
            today_category = category
            today_count = len(valid_tweets)
            avg_engagement = sum(t['engagement_score'] for t in valid_tweets) / len(valid_tweets)
            print(f"   🎯 {category}: {today_count} 條推文 (平均互動: {avg_engagement:.1f})")
            break
    
    if today_count > 0:
        print(f"\n✅ 保守策略運行成功！")
        print(f"📅 明日將輪替到下一個賽道")
        print(f"🛡️ 確保完全符合Free Tier所有限制")
    else:
        print(f"\n⚠️ 今日未獲得推文或已達使用限制")

if __name__ == "__main__":
    main()