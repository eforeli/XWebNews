#!/usr/bin/env python3
import tweepy
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import random

class ImprovedWeb3Crawler:
    def __init__(self, bearer_token: str):
        """
        改進版Web3 Twitter爬蟲 - 優化關鍵字和策略
        """
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 改進版Web3賽道關鍵字 - 使用更熱門、更容易搜到的詞
        self.web3_categories = {
            "DeFi": {
                "primary": ["DeFi", "Uniswap", "Compound", "Aave"],  # 最熱門的詞
                "secondary": ["DEX", "yield farming", "liquidity", "lending"],
                "tokens": ["UNI", "COMP", "AAVE", "CRV"]
            },
            "Layer1_Layer2": {
                "primary": ["Ethereum", "Solana", "Polygon", "Arbitrum"], 
                "secondary": ["Layer2", "scaling", "rollup", "sidechain"],
                "tokens": ["ETH", "SOL", "MATIC", "ARB"]
            },
            "NFT_GameFi": {
                "primary": ["NFT", "OpenSea", "gaming", "metaverse"],
                "secondary": ["collectibles", "GameFi", "play to earn", "P2E"],
                "tokens": ["AXS", "SAND", "MANA", "ENJ"]
            },
            "AI_Crypto": {
                "primary": ["AI", "ChatGPT", "artificial intelligence", "machine learning"],
                "secondary": ["AI crypto", "neural network", "ML"],
                "tokens": ["FET", "AGIX", "OCEAN", "GRT"]
            },
            "RWA": {
                "primary": ["RWA", "tokenization", "BlackRock", "asset tokenization"],
                "secondary": ["real world assets", "commodities", "bonds"],
                "tokens": ["USDC", "USDT", "DAI"]  # 穩定幣也算RWA
            },
            "Meme_Coins": {
                "primary": ["DOGE", "SHIB", "PEPE", "meme"],
                "secondary": ["Dogecoin", "Shiba Inu", "meme coin", "community"],
                "tokens": ["DOGE", "SHIB", "PEPE", "FLOKI"]
            },
            "Infrastructure": {
                "primary": ["Chainlink", "oracle", "bridge", "cross chain"],
                "secondary": ["interoperability", "Web3 infrastructure", "validator"],
                "tokens": ["LINK", "DOT", "ATOM", "AVAX"]
            }
        }

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('improved_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def build_smart_query(self, category: str, config: Dict) -> str:
        """
        構建智能查詢字符串 - 混合使用不同類型的關鍵字
        """
        # 策略：使用最熱門的primary關鍵字，配合一些token符號
        primary_terms = config["primary"][:1]  # 只用1個最熱門的詞，避免複雜查詢
        
        # 構建簡單查詢
        query = primary_terms[0]
        
        # 添加基本過濾條件 
        query += " -is:retweet"  # 排除轉推
        query += " lang:en"      # 只要英文
        
        # 針對不同類別添加特定過濾
        if category == "Meme_Coins":
            query += " (gain OR pump OR moon OR rocket)"  # meme幣常用詞
        elif category == "DeFi":
            query += " (protocol OR yield OR farm)"       # DeFi常用詞
        elif category == "NFT_GameFi":
            query += " (mint OR collection OR game)"      # NFT/游戲常用詞
        
        return query

    def search_tweets_improved(self, category: str, config: Dict, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        改進版推文搜尋 - 多策略嘗試
        """
        tweets_data = []
        
        # 策略1：智能查詢
        query = self.build_smart_query(category, config)
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🎯 搜尋 {category} (嘗試 {attempt + 1}/{max_retries})")
                self.logger.info(f"   查詢: {query}")
                
                response = self.client.search_recent_tweets(
                    query=query,
                    tweet_fields=['created_at', 'author_id', 'public_metrics'],
                    user_fields=['username', 'verified', 'public_metrics'],
                    expansions=['author_id'],
                    max_results=min(max_results, 100)
                )
                
                if not response or not response.data:
                    self.logger.warning(f"   📉 {category}: 查詢無結果")
                    # 策略2：降級查詢 - 使用更簡單的關鍵字
                    if attempt == 0:
                        query = config["primary"][0]  # 只用一個最熱門的詞
                        continue
                    else:
                        break
                
                tweets = response.data
                users = {}
                if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                    users = {user.id: user for user in response.includes['users']}
                
                for tweet in tweets:
                    author = users.get(tweet.author_id)
                    
                    # 計算熱度分數
                    engagement_score = (
                        tweet.public_metrics['like_count'] * 1 +
                        tweet.public_metrics['retweet_count'] * 2 +
                        tweet.public_metrics['reply_count'] * 0.5
                    )
                    
                    tweet_data = {
                        'category': category,
                        'tweet_id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'author_id': tweet.author_id,
                        'username': getattr(author, 'username', 'unknown') if author else 'unknown',
                        'verified': getattr(author, 'verified', False) if author else False,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                        'engagement_score': engagement_score,
                        'url': f"https://twitter.com/{getattr(author, 'username', 'unknown') if author else 'unknown'}/status/{tweet.id}"
                    }
                    tweets_data.append(tweet_data)
                
                # 按熱度排序
                tweets_data.sort(key=lambda x: x['engagement_score'], reverse=True)
                tweets_data = tweets_data[:max_results]
                
                self.logger.info(f"   ✅ {category}: 找到 {len(tweets_data)} 條推文")
                return tweets_data
                
            except tweepy.TooManyRequests as e:
                self.logger.warning(f"   ⚠️ {category}: API限制，等待...")
                wait_time = 60 + random.uniform(0, 30)  # 等待60-90秒
                time.sleep(wait_time)
                
            except Exception as e:
                self.logger.error(f"   ❌ {category}: {str(e)}")
                if attempt == max_retries - 1:
                    break
                time.sleep(5)
        
        return tweets_data

    def crawl_all_balanced(self, tweets_per_category: int = 15) -> Dict[str, List[Dict[str, Any]]]:
        """
        平衡爬取所有賽道 - 每個賽道都有機會
        """
        self.logger.info("🚀 開始平衡式Web3賽道爬取...")
        
        all_tweets = {}
        total_crawled = 0
        
        # 隨機順序，避免總是某些類別失敗
        categories_list = list(self.web3_categories.items())
        random.shuffle(categories_list)
        
        for category, config in categories_list:
            self.logger.info(f"📊 處理 {category} 類別...")
            
            tweets = self.search_tweets_improved(category, config, tweets_per_category)
            all_tweets[category] = tweets
            
            if tweets:
                total_crawled += len(tweets)
                self.logger.info(f"✅ {category}: 成功 {len(tweets)} 條，累計 {total_crawled}")
            else:
                self.logger.warning(f"⚠️ {category}: 未獲得推文")
            
            # 動態延遲：根據成功率調整
            remaining = len(categories_list) - (list(categories_list).index((category, config)) + 1)
            if remaining > 0:
                # 增加延遲到 2-3 分鐘，確保 API 限制重置
                delay = random.uniform(120, 180)  # 2-3分鐘隨機延遲
                self.logger.info(f"⏰ 等待 {delay:.1f}s 避免API限制，剩餘 {remaining} 個類別...")
                time.sleep(delay)
        
        self.logger.info(f"🎉 平衡爬取完成！總計 {total_crawled} 條推文")
        
        # 顯示各類別結果
        for category, tweets in all_tweets.items():
            if tweets:
                avg_engagement = sum(t['engagement_score'] for t in tweets) / len(tweets)
                self.logger.info(f"📈 {category}: {len(tweets)}條，平均熱度 {avg_engagement:.1f}")
        
        return all_tweets

    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """保存數據為JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"improved_web3_tweets_{timestamp}.json"
            
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
            filename = f"improved_web3_tweets_{timestamp}.csv"
            
        try:
            # 展平所有推文數據
            all_tweets = []
            for category, tweets in data.items():
                all_tweets.extend(tweets)
                
            if all_tweets:
                # 按熱度排序
                all_tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
                
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
    
    print("🚀 改進版Web3多賽道爬蟲")
    print("="*50)
    print("🎯 目標：確保每個賽道都能獲得推文")
    print("🔧 策略：優化關鍵字 + 智能延遲 + 熱度排序")
    print("="*50)
    
    # 創建改進版爬蟲
    crawler = ImprovedWeb3Crawler(BEARER_TOKEN)
    
    # 執行平衡爬取
    all_tweets = crawler.crawl_all_balanced(tweets_per_category=15)  # 每類15條，總計約105條
    
    # 保存數據
    crawler.save_to_json(all_tweets)
    crawler.save_to_csv(all_tweets)
    
    # 顯示詳細統計
    print("\n📊 各賽道爬取結果：")
    total_tweets = 0
    successful_categories = 0
    
    for category, tweets in all_tweets.items():
        if tweets:
            successful_categories += 1
            total_tweets += len(tweets)
            avg_engagement = sum(t.get('engagement_score', 0) for t in tweets) / len(tweets)
            print(f"   ✅ {category}: {len(tweets)} 條推文 (平均熱度: {avg_engagement:.1f})")
        else:
            print(f"   ❌ {category}: 0 條推文")
    
    print(f"\n🎉 成功覆蓋 {successful_categories}/{len(all_tweets)} 個賽道")
    print(f"📈 總計獲得 {total_tweets} 條高質量推文")
    
    if successful_categories >= 5:
        print("✅ 多賽道覆蓋成功！可以生成豐富的新聞報告")
    else:
        print("⚠️ 部分賽道未成功，可能需要調整關鍵字或稍後重試")

if __name__ == "__main__":
    main()