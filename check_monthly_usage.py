#!/usr/bin/env python3
"""
檢查本月API使用量和額度狀況
"""

import os
import json
from datetime import datetime
import glob

def estimate_usage_from_files():
    """從現有檔案估算使用量"""
    
    print("📊 估算本月API使用量")
    print("=" * 50)
    
    current_month = datetime.now().strftime("%Y-%m")
    print(f"🗓️ 當前月份: {current_month}")
    
    # 檢查各種推文數據檔案
    file_patterns = [
        "web3_tweets_*.json",
        "rotational_web3_*.json", 
        "full_coverage_web3_*.json",
        "hybrid_daily_*.json",
        "free_tier_*.json",
        "safe_free_*.json"
    ]
    
    total_estimated_posts = 0
    files_checked = 0
    
    for pattern in file_patterns:
        files = glob.glob(pattern)
        
        for file in files:
            try:
                # 檢查檔案修改時間是否在本月
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if file_time.strftime("%Y-%m") == current_month:
                    
                    # 嘗試讀取檔案並計算推文數
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    file_posts = 0
                    if isinstance(data, dict):
                        for category, tweets in data.items():
                            if isinstance(tweets, list):
                                # 過濾掉非推文項目
                                valid_tweets = [t for t in tweets if isinstance(t, dict) and 'tweet_id' in t]
                                file_posts += len(valid_tweets)
                    
                    if file_posts > 0:
                        print(f"   📁 {file}: {file_posts} 條推文 ({file_time.strftime('%m-%d %H:%M')})")
                        total_estimated_posts += file_posts
                        files_checked += 1
                        
            except Exception as e:
                continue
    
    print(f"\n📈 估算結果:")
    print(f"   檢查檔案數: {files_checked}")
    print(f"   估算本月獲取推文數: {total_estimated_posts}")
    print(f"   Free Tier限制: 100 Posts/月")
    
    if total_estimated_posts == 0:
        print(f"   📊 狀態: 未找到本月使用記錄")
        print(f"   💡 可能原因: 檔案太舊或使用量追蹤尚未建立")
    elif total_estimated_posts < 50:
        print(f"   ✅ 狀態: 額度充足 ({100 - total_estimated_posts} 條剩餘)")
    elif total_estimated_posts < 90:
        print(f"   ⚠️ 狀態: 額度偏緊 ({100 - total_estimated_posts} 條剩餘)")
    elif total_estimated_posts >= 100:
        print(f"   🚫 狀態: 疑似額度已滿 (超出 {total_estimated_posts - 100} 條)")
        print(f"   💡 注意: 這可能解釋了為什麼API一直被限制")
    else:
        print(f"   ⚠️ 狀態: 接近額度上限 ({100 - total_estimated_posts} 條剩餘)")
    
    return total_estimated_posts

def check_api_current_status():
    """檢查API當前狀態"""
    print(f"\n🔍 當前API狀態檢查:")
    
    try:
        import subprocess
        result = subprocess.run(['python3', 'check_api_limits.py'], 
                              capture_output=True, text=True)
        
        if "API 正常運作" in result.stdout:
            print("   ✅ API目前可用")
            return "available"
        elif "API 達到限制" in result.stdout:
            print("   ❌ API目前被限制")
            return "rate_limited"
        else:
            print("   ❓ API狀態不明")
            return "unknown"
            
    except Exception as e:
        print(f"   ❌ 無法檢查API狀態: {str(e)}")
        return "error"

def analyze_situation(estimated_posts, api_status):
    """分析當前狀況"""
    
    print(f"\n🎯 狀況分析:")
    
    if estimated_posts >= 100 and api_status == "rate_limited":
        print("   🚨 高機率已達月度限制 (100 Posts/月)")
        print("   💡 這解釋了為什麼API持續被限制")
        print("   📅 建議等待下月1日重置")
        
    elif estimated_posts < 50 and api_status == "rate_limited":
        print("   🤔 可能是rate limit問題 (1次/15分鐘)")
        print("   💡 今晚的測試可能觸發了rate limiting")
        print("   ⏰ 建議等待15分鐘後再試")
        
    elif estimated_posts >= 50 and estimated_posts < 100:
        print("   ⚠️ 額度偏緊，需謹慎使用")
        print("   💡 建議使用保守策略(每次10條)")
        
    else:
        print("   ❓ 狀況不明確，需要實際測試驗證")

def main():
    print("📋 Free Tier使用量檢查工具")
    print("=" * 50)
    
    # 估算使用量
    estimated_posts = estimate_usage_from_files()
    
    # 檢查API狀態
    api_status = check_api_current_status()
    
    # 分析狀況
    analyze_situation(estimated_posts, api_status)
    
    print(f"\n💡 建議:")
    if estimated_posts >= 100:
        print("   - 等待下月1日額度重置")
        print("   - 或考慮升級到Basic Tier ($200/月)")
    else:
        print("   - 使用保守爬蟲策略")
        print("   - 每次只獲取10條推文")
        print("   - 建立使用量追蹤機制")

if __name__ == "__main__":
    main()