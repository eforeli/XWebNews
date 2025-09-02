#!/usr/bin/env python3
"""
等待並測試 - 監控API狀態，重置後立即測試全覆蓋爬蟲
"""

import time
import subprocess
from datetime import datetime, timedelta

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
    
    print("⏰ 等待API限制重置...")
    print("=" * 50)
    
    start_time = datetime.now()
    max_wait_time = 20 * 60  # 最多等待20分鐘
    check_interval = 30  # 每30秒檢查一次
    
    print(f"🕒 開始等待時間: {start_time.strftime('%H:%M:%S')}")
    print(f"⏳ 最大等待時間: {max_wait_time//60} 分鐘")
    print(f"🔍 檢查間隔: {check_interval} 秒")
    print()
    
    elapsed = 0
    while elapsed < max_wait_time:
        print(f"🔍 檢查API狀態... (已等待 {elapsed//60}分{elapsed%60}秒)")
        
        if check_api_ready():
            print(f"✅ API已重置！總等待時間: {elapsed//60}分{elapsed%60}秒")
            return True
        
        print(f"   ⏰ API仍受限制，{check_interval}秒後再檢查...")
        time.sleep(check_interval)
        elapsed += check_interval
    
    print(f"❌ 等待超時 ({max_wait_time//60}分鐘)，API可能需要更長時間重置")
    return False

def run_full_coverage_test():
    """執行全覆蓋爬蟲測試"""
    
    print("\n🚀 開始全覆蓋爬蟲測試...")
    print("=" * 50)
    
    try:
        result = subprocess.run(['python3', 'full_coverage_crawler.py'], 
                              capture_output=True, text=True, timeout=1800)  # 30分鐘超時
        
        print("📊 測試執行完成！")
        print("\n--- 執行日誌 ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- 錯誤日誌 ---")
            print(result.stderr)
        
        # 分析結果
        if "覆蓋率:" in result.stdout:
            coverage_line = [line for line in result.stdout.split('\n') if "覆蓋率:" in line]
            if coverage_line:
                print(f"\n🎯 {coverage_line[0]}")
        
        if "總推文:" in result.stdout:
            total_line = [line for line in result.stdout.split('\n') if "總推文:" in line]
            if total_line:
                print(f"📈 {total_line[0]}")
        
        # 判斷成功程度
        success_categories = result.stdout.count("✅")
        if success_categories >= 5:
            print(f"\n🎉 測試成功！{success_categories} 個賽道成功爬取")
            print("✅ 多賽道覆蓋問題已解決！")
        elif success_categories >= 3:
            print(f"\n✅ 部分成功：{success_categories} 個賽道成功")
            print("💡 比之前的單賽道有明顯改善")
        else:
            print(f"\n⚠️ 仍需優化：只有 {success_categories} 個賽道成功")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠️ 測試超時（30分鐘），程序可能還在運行")
        return False
    except Exception as e:
        print(f"❌ 測試執行錯誤: {str(e)}")
        return False

def main():
    print("🔬 API重置等待 & 全覆蓋測試")
    print("=" * 50)
    print("🎯 目標: 驗證多賽道覆蓋爬蟲是否解決問題")
    print("📊 期望: 7個Web3賽道都有推文數據")
    print("=" * 50)
    
    # 步驟1: 等待API重置
    if not wait_for_api_reset():
        print("❌ API未重置，無法進行測試")
        print("💡 建議明天檢查自動排程結果")
        return
    
    # 步驟2: 執行全覆蓋測試
    print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')} - API已重置，開始測試...")
    
    success = run_full_coverage_test()
    
    # 步驟3: 生成測試報告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"wait_and_test_report_{timestamp}.txt"
    
    report_content = f"""
等待並測試報告
=====================================
測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
測試目標: 驗證全覆蓋爬蟲解決多賽道問題

結果: {'成功' if success else '失敗'}
備註: 詳細結果請查看控制台輸出

下一步:
- 檢查生成的 full_coverage_web3_*.json 檔案
- 確認是否有多個賽道的推文數據
- 驗證系統排程設定正確
=====================================
"""
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📋 測試報告已保存: {report_filename}")
    
    if success:
        print("\n🎊 測試完成！多賽道覆蓋問題應該已經解決")
        print("📅 明天早上8:00系統會自動執行相同的全覆蓋爬蟲")
        print("💡 你可以安心關閉terminal了")
    else:
        print("\n⚠️ 測試未完全成功，可能需要進一步調整")

if __name__ == "__main__":
    main()