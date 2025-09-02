#!/usr/bin/env python3
import tweepy
import json
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

class TwitterWeb3Crawler:
    def __init__(self, bearer_token: str):
        """
        初始化Twitter API爬蟲
        
        Args:
            bearer_token: Twitter API Bearer Token
        """
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.setup_logging()
        
        # Web3賽道關鍵字定義
        self.web3_categories = {
            "DeFi": ["DeFi", "DEX", "liquidity", "yield farming", "staking", "AMM", "lending protocol", "UniSwap", "SushiSwap", "Compound"],
            "Layer1_Layer2": ["Ethereum", "Bitcoin", "Solana", "Polygon", "Arbitrum", "Optimism", "scaling", "Layer2", "rollup"],
            "NFT_GameFi": ["NFT", "GameFi", "P2E", "metaverse", "gaming", "collectibles", "OpenSea", "play to earn"],
            "AI_Crypto": ["AI crypto", "machine learning", "artificial intelligence blockchain", "AI token", "GPT", "neural network crypto"],
            "RWA": ["RWA", "tokenization", "real world assets", "commodity", "real estate token", "asset backed"],
            "Meme_Coins": ["meme coin", "DOGE", "SHIB", "community token", "dogecoin", "shiba inu"],
            "Infrastructure": ["Web3 infrastructure", "oracle", "cross-chain", "bridge", "Chainlink", "interoperability"]
        }

    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def search_tweets_by_category(self, category: str, keywords: List[str], max_results: int = 100) -> List[Dict[str, Any]]:
        """
        根據類別和關鍵字搜尋推文
        
        Args:
            category: Web3類別名稱
            keywords: 關鍵字列表
            max_results: 最大結果數量
            
        Returns:
            推文數據列表
        """
        tweets_data = []
        
        # 構建查詢字符串
        query = " OR ".join([f'"{keyword}"' for keyword in keywords])
        query += " -is:retweet lang:en"  # 排除轉推，只要英文推文
        
        try:
            self.logger.info(f"正在搜尋 {category} 類別的推文...")
            
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'verified', 'public_metrics'],
                expansions=['author_id'],
                max_results=min(max_results, 100)
            ).flatten(limit=max_results)
            
            users = {}
            if hasattr(tweets, 'includes') and 'users' in tweets.includes:
                users = {user.id: user for user in tweets.includes['users']}
            
            for tweet in tweets:
                # 獲取用戶信息
                author = users.get(tweet.author_id, {})
                
                tweet_data = {
                    'category': category,
                    'tweet_id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
                    'username': getattr(author, 'username', 'unknown'),
                    'verified': getattr(author, 'verified', False),
                    'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0,
                    'quote_count': tweet.public_metrics['quote_count'] if tweet.public_metrics else 0,
                    'url': f"https://twitter.com/{getattr(author, 'username', 'unknown')}/status/{tweet.id}"
                }
                tweets_data.append(tweet_data)
                
            self.logger.info(f"{category} 類別找到 {len(tweets_data)} 條推文")
            
        except Exception as e:
            self.logger.error(f"搜尋 {category} 時發生錯誤: {str(e)}")
            
        return tweets_data

    def crawl_all_categories(self, tweets_per_category: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """
        爬取所有Web3類別的推文
        
        Args:
            tweets_per_category: 每個類別爬取的推文數量
            
        Returns:
            按類別分組的推文數據
        """
        all_tweets = {}
        
        for category, keywords in self.web3_categories.items():
            self.logger.info(f"開始爬取 {category} 類別...")
            tweets = self.search_tweets_by_category(category, keywords, tweets_per_category)
            all_tweets[category] = tweets
            
            # API限制：避免過於頻繁的請求
            time.sleep(5)  # 增加延遲時間，避免觸發429錯誤
            
        return all_tweets

    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """保存數據為JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"web3_tweets_{timestamp}.json"
            
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"數據已保存到 {filename}")
        except Exception as e:
            self.logger.error(f"保存JSON文件時發生錯誤: {str(e)}")

    def save_to_csv(self, data: Dict[str, List[Dict[str, Any]]], filename: str = None):
        """保存數據為CSV文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"web3_tweets_{timestamp}.csv"
            
        try:
            # 展平所有推文數據
            all_tweets = []
            for category, tweets in data.items():
                all_tweets.extend(tweets)
                
            if all_tweets:
                fieldnames = all_tweets[0].keys()
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_tweets)
                    
                self.logger.info(f"數據已保存到 {filename}")
            else:
                self.logger.warning("沒有數據可保存")
                
        except Exception as e:
            self.logger.error(f"保存CSV文件時發生錯誤: {str(e)}")

    def analyze_trending_topics(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """分析熱門主題和趨勢"""
        analysis = {
            'category_stats': {},
            'top_tweets': {},
            'trending_keywords': {},
            'summary': {}
        }
        
        total_tweets = 0
        
        for category, tweets in data.items():
            if not tweets:
                continue
                
            # 類別統計
            category_stats = {
                'tweet_count': len(tweets),
                'avg_likes': sum(tweet['like_count'] for tweet in tweets) / len(tweets),
                'avg_retweets': sum(tweet['retweet_count'] for tweet in tweets) / len(tweets),
                'verified_users': sum(1 for tweet in tweets if tweet['verified'])
            }
            analysis['category_stats'][category] = category_stats
            total_tweets += len(tweets)
            
            # 熱門推文（按讚數排序）
            top_tweets = sorted(tweets, key=lambda x: x['like_count'], reverse=True)[:5]
            analysis['top_tweets'][category] = top_tweets
            
        # 總結
        analysis['summary'] = {
            'total_tweets': total_tweets,
            'categories_covered': len([cat for cat, tweets in data.items() if tweets]),
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis

def main():
    # Twitter API Bearer Token
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    
    if not BEARER_TOKEN:
        print("請先設定你的Twitter API Bearer Token")
        return
    
    # 創建爬蟲實例
    crawler = TwitterWeb3Crawler(BEARER_TOKEN)
    
    print("開始爬取Web3相關推文...")
    
    # 爬取所有類別的推文
    all_tweets = crawler.crawl_all_categories(tweets_per_category=50)
    
    # 保存數據
    crawler.save_to_json(all_tweets)
    crawler.save_to_csv(all_tweets)
    
    # 分析趨勢
    analysis = crawler.analyze_trending_topics(all_tweets)
    crawler.save_to_json(analysis, "web3_analysis.json")
    
    # 顯示簡要統計
    print("\n=== 爬取結果摘要 ===")
    for category, tweets in all_tweets.items():
        if tweets:
            print(f"{category}: {len(tweets)} 條推文")
    
    print(f"\n總共爬取了 {analysis['summary']['total_tweets']} 條推文")
    print("數據已保存到JSON和CSV文件中")

if __name__ == "__main__":
    main()