#!/usr/bin/env python3
"""
檢查 Twitter API 限制狀況
"""

import tweepy
from datetime import datetime

def check_api_status():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    
    print("🔍 檢查 Twitter API 限制狀況...")
    print("=" * 50)
    
    try:
        # 嘗試最簡單的查詢
        response = client.search_recent_tweets(
            query="Bitcoin",
            max_results=10
        )
        
        if response and response.data:
            print(f"✅ API 正常運作")
            print(f"📊 成功獲得 {len(response.data)} 條推文")
            print(f"🕒 檢查時間: {datetime.now().strftime('%H:%M:%S')}")
            
            # 顯示第一條推文作為驗證
            first_tweet = response.data[0]
            print(f"📝 範例推文: {first_tweet.text[:100]}...")
            
        else:
            print("⚠️ API 回應為空")
            
    except tweepy.TooManyRequests as e:
        print("❌ API 達到限制")
        print("💡 Twitter API v2 限制: 每15分鐘300次請求")
        print("💡 可能需要等待約15分鐘重置")
        
    except tweepy.Unauthorized as e:
        print("❌ API 認證失敗")
        print("💡 請檢查 Bearer Token 是否正確")
        
    except Exception as e:
        print(f"❌ 其他錯誤: {str(e)}")

if __name__ == "__main__":
    check_api_status()