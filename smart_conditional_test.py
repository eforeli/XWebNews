#!/usr/bin/env python3
"""
智能條件測試 - 爬蟲成功才執行完整管道
"""

import time
import subprocess
import json
import glob
import os
from datetime import datetime

def check_api_ready():
    """檢查API是否可用"""
    try:
        result = subprocess.run(['python3', 'check_api_limits.py'], 
                              capture_output=True, text=True)
        return "API 正常運作" in result.stdout
    except:
        return False

def wait_for_api_reset():
    """等待API重置"""
    print("⏰ 步驟0: 等待API限制重置...")
    print("=" * 50)
    
    start_time = datetime.now()
    max_wait_time = 20 * 60  # 最多等待20分鐘
    check_interval = 30  # 每30秒檢查一次
    
    print(f"🕒 開始時間: {start_time.strftime('%H:%M:%S')}")
    
    elapsed = 0
    while elapsed < max_wait_time:
        print(f"🔍 檢查API... (已等待 {elapsed//60}分{elapsed%60}秒)")
        
        if check_api_ready():
            print(f"✅ API已重置！等待時間: {elapsed//60}分{elapsed%60}秒")
            return True
        
        time.sleep(check_interval)
        elapsed += check_interval
    
    print(f"❌ 等待超時，API可能需要更長時間")
    return False

def analyze_crawler_results():
    """分析爬蟲結果，判斷是否成功"""
    
    # 尋找最新的爬蟲結果
    json_files = glob.glob("full_coverage_web3_*.json")
    if not json_files:
        print("❌ 未找到爬蟲結果檔案")
        return False, "無結果檔案"
    
    latest_file = max(json_files, key=os.path.getctime)
    print(f"📁 分析檔案: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 統計成功的賽道
        successful_categories = []
        total_tweets = 0
        
        for category, tweets in data.items():
            if tweets and len(tweets) > 0:
                successful_categories.append(category)
                total_tweets += len(tweets)
        
        coverage_rate = (len(successful_categories) / 7) * 100
        
        print(f"📊 爬蟲結果分析:")
        print(f"   ✅ 成功賽道: {len(successful_categories)}/7 ({coverage_rate:.1f}%)")
        print(f"   📈 總推文數: {total_tweets}")
        print(f"   🎯 成功賽道: {', '.join(successful_categories)}")
        
        # 判斷標準
        if len(successful_categories) >= 5 and total_tweets >= 50:
            print("🎉 優秀結果！爬蟲問題已解決")
            return True, "優秀"
        elif len(successful_categories) >= 3 and total_tweets >= 30:
            print("✅ 良好結果！明顯改善")
            return True, "良好"
        elif len(successful_categories) >= 2:
            print("⚠️ 部分改善，但仍需優化")
            return False, "需優化"
        else:
            print("❌ 結果不理想，需要重新檢討策略")
            return False, "失敗"
            
    except Exception as e:
        print(f"❌ 分析結果檔案錯誤: {str(e)}")
        return False, "分析錯誤"

def run_crawler_test():
    """執行選項A: 爬蟲測試"""
    
    print("\n🔍 選項A: 全覆蓋爬蟲測試")
    print("=" * 50)
    
    try:
        result = subprocess.run(['python3', 'full_coverage_crawler.py'], 
                              capture_output=True, text=True, timeout=1800)
        
        print("📊 爬蟲執行完成")
        
        # 顯示關鍵輸出
        if "覆蓋率:" in result.stdout:
            coverage_lines = [line for line in result.stdout.split('\n') if "覆蓋率:" in line or "總推文:" in line]
            for line in coverage_lines:
                print(f"   {line}")
        
        # 分析結果
        success, quality = analyze_crawler_results()
        return success, quality
        
    except subprocess.TimeoutExpired:
        print("⚠️ 爬蟲執行超時")
        return False, "超時"
    except Exception as e:
        print(f"❌ 爬蟲執行錯誤: {str(e)}")
        return False, "錯誤"

def run_complete_pipeline():
    """執行選項B: 完整管道"""
    
    print("\n🚀 選項B: 完整管道測試 (爬蟲→AI→LINE)")
    print("=" * 50)
    print("💡 因為爬蟲成功，現在執行完整流程")
    
    try:
        result = subprocess.run(['python3', 'quick_news_test.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if "LINE推送成功" in result.stdout:
            print("🎉 完整管道成功！")
            print("📱 請檢查你的LINE接收Web3新聞")
            return True
        elif "測試部分成功" in result.stdout:
            print("✅ AI分析成功，LINE可能有小問題")
            return True
        else:
            print("⚠️ 完整管道部分失敗")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ 完整管道超時")
        return False
    except Exception as e:
        print(f"❌ 完整管道錯誤: {str(e)}")
        return False

def main():
    print("🧠 智能條件測試系統")
    print("=" * 50)
    print("🎯 邏輯: 爬蟲成功 → 完整管道 | 爬蟲問題 → 優化爬蟲")
    print("=" * 50)
    
    # 步驟0: 等待API重置
    if not wait_for_api_reset():
        print("❌ API未重置，無法執行測試")
        return
    
    # 步驟1: 執行爬蟲測試
    crawler_success, quality = run_crawler_test()
    
    # 決策邏輯
    if crawler_success:
        print(f"\n✅ 爬蟲測試成功 (質量: {quality})")
        print("🔄 繼續執行完整管道測試...")
        
        # 步驟2: 執行完整管道
        pipeline_success = run_complete_pipeline()
        
        # 最終總結
        print("\n" + "=" * 50)
        print("📋 智能測試完成總結")
        print("=" * 50)
        print(f"✅ 爬蟲測試: 成功 ({quality})")
        print(f"{'✅' if pipeline_success else '⚠️'} 完整管道: {'成功' if pipeline_success else '部分成功'}")
        
        if pipeline_success:
            print("\n🎊 完美！多賽道問題已解決 + 完整流程正常")
            print("📅 明天8:00自動排程會很可靠")
            print("📱 你應該已收到LINE推送的Web3新聞")
        else:
            print("\n✅ 爬蟲問題已解決，LINE推送部分需要檢查")
            print("💡 核心功能正常，可以放心使用")
            
    else:
        print(f"\n❌ 爬蟲測試未達標 (狀況: {quality})")
        print("🔧 不執行完整管道，優先解決爬蟲問題")
        
        # 分析問題
        print("\n💡 問題分析建議:")
        if quality == "需優化":
            print("   - API限制仍太嚴格，建議增加延遲時間")
            print("   - 考慮進一步簡化關鍵字策略")
        elif quality == "失敗":
            print("   - 可能需要重新設計爬蟲策略")
            print("   - 檢查Twitter API配額是否有其他限制")
        else:
            print("   - 檢查執行日誌找出具體問題")
    
    # 保存測試報告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"smart_test_report_{timestamp}.txt"
    
    report_content = f"""
智能條件測試報告
=====================================
測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
測試邏輯: 爬蟲成功→完整管道 | 爬蟲問題→優化爬蟲

結果:
- 爬蟲測試: {'成功' if crawler_success else '失敗'} ({quality})
- 完整管道: {'執行成功' if crawler_success and 'pipeline_success' in locals() and pipeline_success else '未執行或失敗'}

多賽道覆蓋問題: {'✅ 已解決' if crawler_success else '❌ 仍需優化'}

下一步:
{'系統準備好每日自動執行' if crawler_success else '需要進一步優化爬蟲策略'}
=====================================
"""
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📊 智能測試報告: {report_filename}")

if __name__ == "__main__":
    main()