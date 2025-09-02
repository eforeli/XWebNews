#!/usr/bin/env python3
"""
自動化測試排程器 - 15分鐘後自動測試API並執行輪替爬蟲
"""

import time
import subprocess
import os
from datetime import datetime, timedelta

def wait_and_test():
    """等待15分鐘後自動測試"""
    
    print("⏰ 自動測試排程器啟動")
    print("=" * 50)
    
    # 計算等待時間
    wait_time = 15 * 60  # 15分鐘 = 900秒
    end_time = datetime.now() + timedelta(seconds=wait_time)
    
    print(f"🕒 當前時間: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🎯 預計執行時間: {end_time.strftime('%H:%M:%S')}")
    print(f"⏳ 等待 {wait_time//60} 分鐘後自動執行...")
    print()
    print("💡 你可以安全關閉 terminal，程式會在背景執行")
    print("📁 結果將保存在當前目錄的日誌檔案中")
    print("=" * 50)
    
    # 等待
    time.sleep(wait_time)
    
    # 執行測試
    print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')} - 開始執行API測試...")
    
    try:
        # 1. 先檢查API狀態
        print("📡 步驟1: 檢查API限制狀態...")
        result1 = subprocess.run(['python3', 'check_api_limits.py'], 
                               capture_output=True, text=True)
        
        log_content = f"""
=== API限制檢查結果 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===
{result1.stdout}
{result1.stderr}

"""
        
        if "API 正常運作" in result1.stdout:
            print("✅ API限制已重置，執行輪替爬蟲...")
            
            # 2. 執行輪替爬蟲
            print("🔄 步驟2: 執行輪替式多賽道爬蟲...")
            result2 = subprocess.run(['python3', 'rotational_crawler.py'], 
                                   capture_output=True, text=True)
            
            log_content += f"""
=== 輪替爬蟲執行結果 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===
{result2.stdout}
{result2.stderr}

"""
            
            if "成功爬取" in result2.stdout and "0 個賽道" not in result2.stdout:
                print("🎉 多賽道爬蟲測試成功！")
                success_msg = "✅ 測試成功：多賽道問題已解決！"
            else:
                print("⚠️ 爬蟲執行完成，但可能仍需調整")
                success_msg = "⚠️ 測試完成：需要檢查日誌確認結果"
                
        else:
            print("❌ API限制仍未重置，可能需要等待更久")
            success_msg = "❌ API限制未重置：可能需要等待更久"
        
        # 3. 保存完整日誌
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"auto_test_log_{timestamp}.txt"
        
        with open(log_filename, 'w', encoding='utf-8') as f:
            f.write(f"自動化測試報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"最終結果: {success_msg}\n\n")
            f.write(log_content)
        
        print(f"📊 完整測試日誌已保存: {log_filename}")
        print(f"🎯 最終結果: {success_msg}")
        
    except Exception as e:
        error_msg = f"執行測試時發生錯誤: {str(e)}"
        print(f"❌ {error_msg}")
        
        # 保存錯誤日誌
        with open(f"auto_test_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'w') as f:
            f.write(f"自動測試錯誤報告\n時間: {datetime.now()}\n錯誤: {error_msg}")

if __name__ == "__main__":
    wait_and_test()