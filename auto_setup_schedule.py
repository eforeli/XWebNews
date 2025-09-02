#!/usr/bin/env python3
"""
自動建立系統排程 - 無需手動輸入
"""

import os
import subprocess
from datetime import datetime

def create_launch_agent():
    """建立 macOS LaunchAgent"""
    
    current_dir = os.getcwd()
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.web3crawler.daily.plist")
    
    # LaunchAgent 設定
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
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>'''
    
    print("🍎 建立 macOS LaunchAgent...")
    print(f"📍 位置: {plist_path}")
    print(f"⏰ 排程: 每日早上 8:00")
    print(f"📁 工作目錄: {current_dir}")
    
    try:
        # 建立目錄
        os.makedirs(os.path.dirname(plist_path), exist_ok=True)
        
        # 寫入 plist
        with open(plist_path, 'w') as f:
            f.write(plist_content)
        
        # 載入服務
        result = subprocess.run(['launchctl', 'load', plist_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ LaunchAgent 建立成功！")
            
            # 驗證
            check_result = subprocess.run(['launchctl', 'list', 'com.web3crawler.daily'], 
                                        capture_output=True, text=True)
            if check_result.returncode == 0:
                print("✅ 服務已正確註冊")
            else:
                print("⚠️ 服務註冊可能有問題")
                
        else:
            print(f"❌ LaunchAgent 載入失敗: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 建立 LaunchAgent 失敗: {str(e)}")
        return False
    
    return True

def create_manual_instructions():
    """建立手動設定說明"""
    
    current_dir = os.getcwd()
    
    instructions = f"""
📋 Web3爬蟲系統排程設定說明
=====================================

🎯 目標: 每日自動執行Web3多賽道爬蟲

📍 資料存儲位置:
- 系統排程: ~/Library/LaunchAgents/com.web3crawler.daily.plist
- 爬蟲程式: {current_dir}/rotational_crawler.py  
- 執行結果: {current_dir}/daily_crawl.log
- 錯誤記錄: {current_dir}/daily_crawl_error.log

⏰ 執行時間: 每日早上 8:00

🔧 手動設定 cron job (備用方案):
1. 執行: crontab -e
2. 加入: 0 8 * * * cd {current_dir} && python3 rotational_crawler.py >> daily_crawl.log 2>&1
3. 儲存退出: :wq

📊 檢查排程狀態:
- LaunchAgent: launchctl list com.web3crawler.daily
- Cron: crontab -l

🗂️ 重要檔案:
- rotational_crawler.py (主程式)
- crawler_rotation_state.json (輪替狀態)
- daily_crawl.log (執行日誌)
- rotational_web3_YYYYMMDD_HHMMSS.json (爬蟲結果)

💡 優勢:
✅ 電腦重開機自動恢復
✅ 系統層級穩定執行  
✅ 完整日誌記錄
✅ 7天週期覆蓋所有Web3賽道

=====================================
建立時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # 保存說明文件
    with open('Web3爬蟲排程說明.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("📋 排程說明已保存到: Web3爬蟲排程說明.txt")
    return instructions

def main():
    print("🚀 自動建立Web3爬蟲系統排程")
    print("=" * 50)
    
    # 建立 LaunchAgent
    success = create_launch_agent()
    
    # 建立說明文件
    instructions = create_manual_instructions()
    
    print("\n" + "=" * 50)
    print("📊 設定完成摘要")
    print("=" * 50)
    
    if success:
        print("✅ macOS LaunchAgent 已成功建立")
        print("⏰ 將於每日早上8:00自動執行")
        print("🔄 系統重開機後自動恢復")
    else:
        print("⚠️ LaunchAgent 建立失敗")
        print("💡 可參考說明文件手動設定 cron job")
    
    print("\n🎯 關鍵優勢:")
    print("✅ 資料永久存儲在系統排程資料庫")
    print("✅ 不依賴terminal，系統層級執行")  
    print("✅ 完整日誌記錄和錯誤處理")
    print("✅ 輪替策略確保多賽道覆蓋")
    
    print(f"\n📁 執行結果查看:")
    print(f"   日誌: daily_crawl.log")
    print(f"   數據: rotational_web3_*.json")
    print(f"   狀態: crawler_rotation_state.json")

if __name__ == "__main__":
    main()