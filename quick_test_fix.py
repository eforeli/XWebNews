#!/usr/bin/env python3
"""
快速測試修復 - 測試前3個賽道的簡化查詢
"""

import tweepy
import time
import json
from datetime import datetime

def test_multi_category_crawling():
    """測試多賽道爬取修復"""
    
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    
    # 簡化的賽道測試 - 只用最熱門關鍵字
    test_categories = {
        "DeFi": "DeFi",
        "Layer1_Layer2": "Ethereum", 
        "NFT_GameFi": "NFT"
    }
    
    results = {}
    
    for i, (category, keyword) in enumerate(test_categories.items()):
        print(f"\n🎯 測試 {category} 類別 (關鍵字: {keyword})")
        
        try:
            query = f"{keyword} -is:retweet lang:en"
            print(f"   查詢: {query}")
            
            response = client.search_recent_tweets(
                query=query,
                tweet_fields=['created_at', 'public_metrics'],
                max_results=10  # 小樣本測試
            )
            
            if response and response.data:
                tweet_count = len(response.data)
                results[category] = tweet_count
                print(f"   ✅ 成功獲得 {tweet_count} 條推文")
            else:
                results[category] = 0
                print(f"   ⚠️ 無推文")
                
        except tweepy.TooManyRequests:
            print(f"   ❌ API限制 - 這說明需要更長延遲")
            results[category] = "API_LIMITED"
            
        except Exception as e:
            print(f"   ❌ 錯誤: {str(e)}")
            results[category] = "ERROR"
            
        # 如果不是最後一個，稍微延遲
        if i < len(test_categories) - 1:
            print("   ⏰ 等待 30 秒...")
            time.sleep(30)
    
    # 結果摘要
    print("\n" + "="*50)
    print("🧪 快速測試結果:")
    
    success_count = 0
    for category, result in results.items():
        if isinstance(result, int) and result > 0:
            print(f"   ✅ {category}: {result} 條推文")
            success_count += 1
        elif result == "API_LIMITED":
            print(f"   ⚠️ {category}: API限制")
        else:
            print(f"   ❌ {category}: 失敗")
    
    if success_count >= 2:
        print(f"\n🎉 修復有效！{success_count}/3 個類別成功")
        print("💡 建議: 增加延遲到 5-10 分鐘可能獲得更好結果")
    elif success_count == 1:
        print(f"\n⚠️ 部分修復：只有 1 個類別成功")  
        print("💡 需要更大的延遲時間")
    else:
        print(f"\n❌ 修復無效：所有類別都失敗")
        print("💡 可能需要不同的策略")
        
    return results

if __name__ == "__main__":
    test_multi_category_crawling()