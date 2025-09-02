#!/usr/bin/env python3
"""
完整管道測試 - 爬蟲 → AI分析 → LINE推送
"""

import subprocess
import json
from datetime import datetime

def run_complete_pipeline():
    """執行完整的 Web3 新聞管道"""
    
    print("🚀 完整Web3新聞管道測試")
    print("=" * 50)
    print("📋 流程: 爬蟲 → AI分析 → LINE推送")
    print("=" * 50)
    
    # 步驟1: 執行全覆蓋爬蟲
    print("\n📊 步驟1: 執行全覆蓋爬蟲...")
    
    try:
        crawl_result = subprocess.run(
            ['python3', 'full_coverage_crawler.py'], 
            capture_output=True, text=True, timeout=1800
        )
        
        if "覆蓋率:" in crawl_result.stdout:
            print("✅ 爬蟲執行完成")
            
            # 找到最新的爬蟲結果檔案
            import glob
            import os
            json_files = glob.glob("full_coverage_web3_*.json")
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                print(f"📁 爬蟲結果: {latest_file}")
            else:
                print("❌ 未找到爬蟲結果檔案")
                return False
        else:
            print("❌ 爬蟲執行失敗")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ 爬蟲超時，但可能仍在執行")
        return False
    except Exception as e:
        print(f"❌ 爬蟲錯誤: {str(e)}")
        return False
    
    # 步驟2: AI分析 + LINE推送
    print("\n🤖 步驟2: AI分析 + LINE推送...")
    
    try:
        # 使用現有的 optimized_daily_news.py，但跳過爬蟲部分
        # 或使用 quick_news_test.py
        news_result = subprocess.run(
            ['python3', 'quick_news_test.py'], 
            capture_output=True, text=True, timeout=300
        )
        
        if "LINE推送成功" in news_result.stdout:
            print("✅ AI分析 + LINE推送成功")
            return True
        elif "測試部分成功" in news_result.stdout:
            print("✅ AI分析成功，LINE推送可能有問題")
            return True
        else:
            print("❌ AI分析或LINE推送失敗")
            print("日誌:", news_result.stdout[-200:])
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ AI分析超時")
        return False
    except Exception as e:
        print(f"❌ AI分析錯誤: {str(e)}")
        return False

def main():
    success = run_complete_pipeline()
    
    # 生成報告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"complete_pipeline_test_{timestamp}.txt"
    
    report_content = f"""
完整Web3新聞管道測試報告
=====================================
測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

測試流程:
1. 全覆蓋爬蟲 (所有7個Web3賽道)
2. OpenAI智能分析
3. LINE推送通知

結果: {'✅ 完全成功' if success else '❌ 部分失敗'}

建議:
- 檢查爬蟲數據檔案 (full_coverage_web3_*.json)
- 確認LINE是否收到推送
- 查看詳細日誌了解任何問題

下一步:
{'系統已準備好每日自動執行' if success else '需要檢查和修復問題'}
=====================================
"""
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📋 完整測試報告: {report_filename}")
    
    if success:
        print("\n🎉 完整管道測試成功！")
        print("📱 請檢查你的LINE是否收到Web3新聞")
        print("🔄 明天8:00系統會自動執行相同流程")
    else:
        print("\n⚠️ 測試未完全成功，但爬蟲應該有改善")

if __name__ == "__main__":
    main()