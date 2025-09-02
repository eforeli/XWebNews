#!/usr/bin/env python3
"""
混合每日爬蟲 - Free Tier下每日涵蓋所有賽道
策略：使用混合關鍵字 + 智能分類，1次API請求涵蓋多賽道
"""

import tweepy
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Any
import logging

class HybridDailyCrawler:
    def __init__(self, bearer_token: str):
        """混合每日爬蟲 - 1次請求涵蓋所有賽道"""
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # 混合關鍵字策略 - 涵蓋所有賽道的熱門詞
        self.hybrid_query = "DeFi OR NFT OR Ethereum OR AI OR DOGE OR RWA OR Chainlink"
        
        # 賽道關鍵字映射 - 用於分類推文
        self.category_keywords = {
            "DeFi": [
                "DeFi", "defi", "uniswap", "compound", "aave", "liquidity", 
                "yield", "farming", "staking", "DEX", "AMM", "protocol"
            ],
            "Layer1_Layer2": [
                "Ethereum", "Bitcoin", "Solana", "Polygon", "Arbitrum", 
                "Optimism", "ETH", "BTC", "SOL", "MATIC", "layer2", "scaling"
            ],
            "NFT_GameFi": [
                "NFT", "OpenSea", "gaming", "metaverse", "GameFi", "P2E", 
                "play to earn", "collectibles", "art", "mint", "collection"
            ],
            "AI_Crypto": [
                "AI", "artificial intelligence", "ChatGPT", "machine learning",
                "neural", "GPT", "AI crypto", "ML", "automation", "bot"
            ],
            "RWA": [
                "RWA", "tokenization", "BlackRock", "real world assets", 
                "commodities", "bonds", "asset backed", "traditional assets"
            ],
            "Meme_Coins": [
                "DOGE", "SHIB", "PEPE", "meme", "Dogecoin", "Shiba", 
                "community", "pump", "moon", "diamond hands", "hodl"
            ],
            "Infrastructure": [
                "Chainlink", "oracle", "bridge", "cross chain", "interoperability",
                "infrastructure", "node", "validator", "consensus", "protocol"
            ]
        }

    def setup_logging(self):
        """設置日誌"""
        timestamp = datetime.now().strftime("%Y%m%d")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'hybrid_daily_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def classify_tweet(self, text: str) -> str:
        """智能分類推文到對應賽道"""
        text_lower = text.lower()
        
        # 計算每個賽道的匹配分數
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # 給予不同權重
                    if keyword.lower() in ["defi", "nft", "ethereum", "ai", "doge", "rwa", "chainlink"]:
                        score += 3  # 主關鍵字高權重
                    else:
                        score += 1  # 相關關鍵字低權重
            
            if score > 0:
                category_scores[category] = score
        
        # 返回分數最高的賽道
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            return best_category[0]
        else:
            return "Infrastructure"  # 默認分類

    def crawl_hybrid_daily(self) -> Dict[str, List[Dict[str, Any]]]:
        """執行混合每日爬取"""
        
        self.logger.info("🌍 混合每日Web3爬取")
        self.logger.info("🎯 策略: 1次API請求 → 智能分類到所有賽道")
        self.logger.info(f"🔍 混合查詢: {self.hybrid_query}")
        
        try:
            # 使用混合查詢，最大化利用這1次API請求
            response = self.client.search_recent_tweets(
                query=f"{self.hybrid_query} -is:retweet lang:en",
                tweet_fields=['created_at', 'author_id', 'public_metrics'],
                user_fields=['username', 'verified', 'public_metrics'],
                expansions=['author_id'],
                max_results=100  # 獲取最多推文
            )
            
            if not response or not response.data:
                self.logger.warning("⚠️ 無推文結果")
                return {category: [] for category in self.category_keywords.keys()}
            
            # 處理用戶信息
            users = {}
            if hasattr(response, 'includes') and response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            # 初始化賽道字典
            categorized_tweets = {category: [] for category in self.category_keywords.keys()}
            
            # 處理和分類每條推文
            for tweet in response.data:
                author = users.get(tweet.author_id)
                metrics = tweet.public_metrics or {}
                
                # 智能分類
                category = self.classify_tweet(tweet.text)
                
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
                    'url': f"https://twitter.com/{getattr(author, 'username', 'unknown') if author else 'unknown'}/status/{tweet.id}",
                    'classification_confidence': 'high' if any(kw.lower() in tweet.text.lower() 
                                                             for kw in self.category_keywords[category][:3]) else 'medium'
                }
                
                categorized_tweets[category].append(tweet_data)
            
            # 對每個賽道的推文按互動度排序，取前10條
            for category in categorized_tweets:
                categorized_tweets[category].sort(
                    key=lambda x: x['engagement_score'], reverse=True
                )
                categorized_tweets[category] = categorized_tweets[category][:10]
            
            # 顯示分類結果
            total_tweets = sum(len(tweets) for tweets in categorized_tweets.values())
            self.logger.info(f"✅ 成功分類 {total_tweets} 條推文到各賽道:")
            
            covered_categories = 0
            for category, tweets in categorized_tweets.items():
                if tweets:
                    covered_categories += 1
                    avg_engagement = sum(t['engagement_score'] for t in tweets) / len(tweets)
                    self.logger.info(f"   🎯 {category}: {len(tweets)} 條 (平均互動: {avg_engagement:.1f})")
                else:
                    self.logger.info(f"   ⚪ {category}: 0 條")
            
            coverage_rate = (covered_categories / len(self.category_keywords)) * 100
            self.logger.info(f"📊 賽道覆蓋率: {coverage_rate:.1f}% ({covered_categories}/7)")
            
            return categorized_tweets
            
        except tweepy.TooManyRequests:
            self.logger.error("❌ API限制 - Free tier每15分鐘只能1次請求")
            return {category: [] for category in self.category_keywords.keys()}
        except Exception as e:
            self.logger.error(f"❌ 爬取錯誤: {str(e)}")
            return {category: [] for category in self.category_keywords.keys()}

    def save_results(self, data: Dict[str, List[Dict[str, Any]]]):
        """保存結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 保存
        json_filename = f"hybrid_daily_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # CSV 保存 (所有賽道合併)
        all_tweets = []
        for category, tweets in data.items():
            all_tweets.extend(tweets)
        
        if all_tweets:
            # 按互動度排序
            all_tweets.sort(key=lambda x: x.get('engagement_score', 0), reverse=True)
            
            csv_filename = f"hybrid_daily_{timestamp}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_tweets[0].keys())
                writer.writeheader()
                writer.writerows(all_tweets)
        
        self.logger.info(f"💾 結果已保存: {json_filename}")
        return json_filename

def main():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🌍 混合每日Web3爬蟲")
    print("=" * 50)
    print("🎯 創新策略: 1次API請求涵蓋所有7個賽道")
    print("🤖 智能分類: 自動將推文分類到對應賽道")
    print("📊 每日覆蓋: 所有賽道都有機會獲得內容")
    print("=" * 50)
    
    crawler = HybridDailyCrawler(BEARER_TOKEN)
    
    # 執行混合爬取
    results = crawler.crawl_hybrid_daily()
    
    # 保存結果
    filename = crawler.save_results(results)
    
    # 顯示詳細統計
    print(f"\n📊 混合每日爬取結果摘要:")
    total_tweets = 0
    covered_categories = 0
    
    for category, tweets in results.items():
        if tweets:
            covered_categories += 1
            total_tweets += len(tweets)
            avg_engagement = sum(t.get('engagement_score', 0) for t in tweets) / len(tweets)
            high_confidence = sum(1 for t in tweets if t.get('classification_confidence') == 'high')
            print(f"   ✅ {category}: {len(tweets)} 條 (高可信度: {high_confidence}, 平均互動: {avg_engagement:.1f})")
        else:
            print(f"   ⚪ {category}: 0 條")
    
    coverage_rate = (covered_categories / 7) * 100
    print(f"\n🎉 每日覆蓋成果:")
    print(f"   📈 賽道覆蓋: {coverage_rate:.1f}% ({covered_categories}/7)")
    print(f"   📊 總推文數: {total_tweets}")
    print(f"   🔥 API效率: {total_tweets} 條推文/1次請求")
    
    if coverage_rate >= 70:
        print("\n✅ 優秀！成功在Free Tier下實現每日多賽道覆蓋")
        print("🎯 這個策略完美解決了你的需求")
    elif coverage_rate >= 50:
        print("\n✅ 良好！大部分賽道都有覆蓋")
        print("💡 可能需要微調關鍵字提升覆蓋率")
    else:
        print("\n⚠️ 覆蓋率較低，需要優化混合關鍵字策略")

if __name__ == "__main__":
    main()