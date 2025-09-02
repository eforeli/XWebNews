#!/usr/bin/env python3
"""
設定 macOS 系統排程 (cron job)
真正的自動化排程解決方案
"""

import os
import subprocess
from datetime import datetime

def setup_daily_cron():
    """設定每日自動執行的系統排程"""
    
    print("⚙️ 設定系統排程 (cron job)")
    print("=" * 50)
    
    # 獲取當前工作目錄
    current_dir = os.getcwd()
    
    # cron 排程設定
    # 每日早上 8:00 執行輪替爬蟲
    cron_schedule = f"0 8 * * * cd {current_dir} && /usr/bin/python3 rotational_crawler.py >> daily_crawl.log 2>&1"
    
    print("📋 準備設定的排程:")
    print(f"   時間: 每日早上 8:00")
    print(f"   執行: 輪替式Web3爬蟲")
    print(f"   目錄: {current_dir}")
    print(f"   日誌: daily_crawl.log")
    print()
    
    # 顯示 cron 設定指令
    print("🔧 手動設定 cron job 步驟:")
    print("1. 在terminal執行: crontab -e")
    print("2. 加入以下這行:")
    print(f"   {cron_schedule}")
    print("3. 儲存並退出 (按 :wq)")
    print()
    
    # 自動設定選項
    response = input("要自動設定嗎？(y/n): ").lower().strip()
    
    if response == 'y':
        try:
            # 獲取現有 cron jobs
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_cron = result.stdout if result.returncode == 0 else ""
            
            # 檢查是否已有相同排程
            if "rotational_crawler.py" in existing_cron:
                print("⚠️ 發現現有的Web3爬蟲排程")
                overwrite = input("要覆蓋嗎？(y/n): ").lower().strip()
                if overwrite != 'y':
                    print("❌ 已取消設定")
                    return
            
            # 建立新的 cron 設定
            new_cron = existing_cron.rstrip() + '\n' + cron_schedule + '\n'
            
            # 寫入 cron
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)
            
            if process.returncode == 0:
                print("✅ cron job 設定成功！")
                print("📅 將於每日早上8:00自動執行Web3爬蟲")
                print("📁 結果會保存在 daily_crawl.log")
                
                # 驗證設定
                verify_result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                if "rotational_crawler.py" in verify_result.stdout:
                    print("✅ 驗證成功：排程已正確設定")
                else:
                    print("⚠️ 驗證失敗：可能需要手動設定")
                    
            else:
                print("❌ 自動設定失敗，請手動設定")
                
        except Exception as e:
            print(f"❌ 設定錯誤: {str(e)}")
            print("💡 建議手動設定 cron job")
    
    else:
        print("💡 你可以稍後手動設定")

def setup_macos_launchd():
    """設定 macOS LaunchAgent (更現代的方式)"""
    
    print("\n" + "=" * 50)
    print("🍎 macOS LaunchAgent 設定 (推薦)")
    print("=" * 50)
    
    current_dir = os.getcwd()
    
    # LaunchAgent plist 內容
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.web3crawler.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{current_dir}/rotational_crawler.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{current_dir}/daily_crawl.log</string>
    <key>StandardErrorPath</key>
    <string>{current_dir}/daily_crawl_error.log</string>
</dict>
</plist>'''
    
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.web3crawler.daily.plist")
    
    print(f"📁 LaunchAgent 檔案位置:")
    print(f"   {plist_path}")
    print()
    print("🔧 自動建立 LaunchAgent:")
    
    response = input("要建立 macOS LaunchAgent 嗎？(y/n): ").lower().strip()
    
    if response == 'y':
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)
            
            # 寫入 plist 檔案
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # 載入 LaunchAgent
            subprocess.run(['launchctl', 'load', plist_path], check=True)
            
            print("✅ macOS LaunchAgent 設定成功！")
            print("🎯 特色:")
            print("   - 系統重開機後自動恢復")
            print("   - 更穩定的排程機制")
            print("   - 完整的日誌記錄")
            print("   - 每日早上8:00自動執行")
            
        except Exception as e:
            print(f"❌ LaunchAgent 設定失敗: {str(e)}")
            print("💡 可能需要系統管理權限")

def show_current_status():
    """顯示目前排程狀態"""
    
    print("\n" + "=" * 50)  
    print("📊 目前排程狀態")
    print("=" * 50)
    
    # 檢查 cron jobs
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0 and "rotational_crawler" in result.stdout:
            print("✅ cron job: 已設定")
        else:
            print("❌ cron job: 未設定")
    except:
        print("⚠️ cron job: 無法檢查")
    
    # 檢查 LaunchAgent
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.web3crawler.daily.plist")
    if os.path.exists(plist_path):
        print("✅ LaunchAgent: 已設定")
    else:
        print("❌ LaunchAgent: 未設定")

def main():
    print("🤖 Web3爬蟲自動排程設定工具")
    print("=" * 50)
    print("🎯 目標: 建立穩定的每日自動爬取系統")
    print("💾 資料存儲: 系統排程 + 本地檔案")
    print("🔄 執行方式: 系統層級排程服務")
    print("=" * 50)
    
    # 顯示目前狀態
    show_current_status()
    
    # 設定選項
    print("\n選擇設定方式:")
    print("1. cron job (通用Unix/Linux方式)")
    print("2. macOS LaunchAgent (推薦for macOS)")
    print("3. 兩種都設定")
    print("4. 只查看狀態")
    
    choice = input("\n請選擇 (1-4): ").strip()
    
    if choice == '1':
        setup_daily_cron()
    elif choice == '2':
        setup_macos_launchd()
    elif choice == '3':
        setup_daily_cron()
        setup_macos_launchd()
    elif choice == '4':
        print("✅ 僅查看狀態，不做變更")
    else:
        print("❌ 無效選擇")

if __name__ == "__main__":
    main()