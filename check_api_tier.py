#!/usr/bin/env python3
"""
檢查Twitter API tier和具體限制
"""

import tweepy
import requests
import json
from datetime import datetime

def check_api_tier_and_limits():
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAF833wEAAAAAVK2bhuSiu%2FaikoUWzmEQvdS%2BJhE%3DjNPAILRXsZOyy1waEYDjahABCRLjG8d9LLyLMAF0CQ3LCckCPq"
    
    print("🔍 檢查Twitter/X API Tier和限制")
    print("=" * 50)
    
    # 方法1: 嘗試獲取rate limit資訊
    try:
        headers = {
            'Authorization': f'Bearer {BEARER_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # 檢查rate limit狀態
        response = requests.get(
            'https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10',
            headers=headers
        )
        
        print(f"📡 API響應狀態: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API可用")
            
            # 檢查rate limit headers
            rate_limit_remaining = response.headers.get('x-rate-limit-remaining')
            rate_limit_limit = response.headers.get('x-rate-limit-limit')
            rate_limit_reset = response.headers.get('x-rate-limit-reset')
            
            if rate_limit_limit:
                print(f"📊 Rate Limit資訊:")
                print(f"   總限制: {rate_limit_limit} 次/15分鐘")
                print(f"   剩餘: {rate_limit_remaining} 次")
                print(f"   重置時間: {rate_limit_reset}")
                
                # 判斷tier
                limit_num = int(rate_limit_limit)
                if limit_num == 1:
                    print("🆓 檢測到: FREE TIER")
                    print("⚠️ 每15分鐘只能1次請求！")
                elif limit_num == 60:
                    print("💰 檢測到: BASIC TIER ($200/月)")
                elif limit_num == 300:
                    print("💎 檢測到: PRO TIER ($5000/月)")
                else:
                    print(f"❓ 未知tier: {limit_num} 次/15分鐘")
            else:
                print("⚠️ 無法獲取rate limit資訊")
                
        elif response.status_code == 429:
            print("❌ API已達限制")
            
            # 嘗試從error response獲取資訊
            try:
                error_data = response.json()
                print(f"錯誤詳情: {error_data}")
            except:
                pass
                
        else:
            print(f"❌ API錯誤: {response.status_code}")
            try:
                error_data = response.json()
                print(f"錯誤內容: {error_data}")
            except:
                print(f"響應內容: {response.text}")
                
    except Exception as e:
        print(f"❌ 檢查API tier錯誤: {str(e)}")
    
    # 方法2: 使用tweepy檢查
    print(f"\n🔍 使用tweepy檢查...")
    try:
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
        
        # 嘗試簡單請求
        response = client.search_recent_tweets(
            query="Bitcoin",
            max_results=10,
            tweet_fields=['created_at']
        )
        
        if response:
            print("✅ tweepy請求成功")
            print(f"📊 獲得 {len(response.data) if response.data else 0} 條推文")
        else:
            print("⚠️ tweepy請求無結果")
            
    except tweepy.TooManyRequests as e:
        print("❌ tweepy: API達到限制")
        print(f"錯誤: {str(e)}")
    except tweepy.Unauthorized as e:
        print("❌ tweepy: 認證失敗")
        print(f"錯誤: {str(e)}")
    except Exception as e:
        print(f"❌ tweepy錯誤: {str(e)}")

def analyze_usage_implications():
    """分析不同tier對我們使用案例的影響"""
    
    print(f"\n📋 使用案例分析")
    print("=" * 50)
    
    scenarios = {
        "Free Tier (1次/15分)": {
            "爬取7個賽道": "1小時45分鐘",
            "每日總時間": "約2小時", 
            "可行性": "❌ 不實用",
            "建議": "升級到Basic或改變策略"
        },
        "Basic Tier (60次/15分)": {
            "爬取7個賽道": "約5-10分鐘",
            "每日總時間": "15分鐘內完成",
            "可行性": "✅ 完全可行",
            "建議": "適合我們的使用案例"
        },
        "Pro Tier (300次/15分)": {
            "爬取7個賽道": "2-3分鐘",
            "每日總時間": "5分鐘內完成", 
            "可行性": "✅ 超級流暢",
            "建議": "過度規格，除非有商業需求"
        }
    }
    
    for tier, info in scenarios.items():
        print(f"\n🎯 {tier}:")
        for key, value in info.items():
            print(f"   {key}: {value}")

def main():
    check_api_tier_and_limits()
    analyze_usage_implications()
    
    print(f"\n💡 解決方案建議:")
    print("1. 確認當前tier級別")
    print("2. 如果是Free tier，考慮升級到Basic ($200/月)")
    print("3. 或設計更保守的爬取策略 (輪替式，每日1-2個賽道)")
    print("4. 實施更長的延遲時間 (如果是Free tier)")

if __name__ == "__main__":
    main()