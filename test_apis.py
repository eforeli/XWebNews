#!/usr/bin/env python3
import openai
import requests
import json

def test_openai_connection(api_key):
    """測試OpenAI API連接"""
    print("🔍 測試OpenAI API連接...")
    
    try:
        openai.api_key = api_key
        
        # 測試API連接
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "請回答：測試成功"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API連接成功")
        print(f"   回應: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API連接失敗: {str(e)}")
        
        if "Unauthorized" in str(e):
            print("   💡 可能原因: API Key不正確")
        elif "insufficient_quota" in str(e) or "billing" in str(e).lower():
            print("   💡 可能原因: 帳戶餘額不足，請前往OpenAI充值")
        elif "rate_limit" in str(e).lower():
            print("   💡 可能原因: 請求太頻繁，請稍後再試")
            
        return False

def test_line_connection(access_token, user_id):
    """測試LINE API連接"""
    print("\n🔍 測試LINE API連接...")
    
    try:
        # 測試發送訊息
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': '🤖 API測試訊息 - 如果你收到這則訊息，表示設定成功！'
                }
            ]
        }
        
        response = requests.post(
            'https://api.line.me/v2/bot/message/push',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ LINE API連接成功")
            print("   📱 測試訊息已發送到你的LINE")
            return True
        else:
            print(f"❌ LINE API連接失敗: {response.status_code}")
            print(f"   錯誤詳情: {response.text}")
            
            if response.status_code == 401:
                print("   💡 可能原因: Channel Access Token不正確")
            elif response.status_code == 400:
                print("   💡 可能原因: User ID格式錯誤或用戶已封鎖Bot")
                
            return False
            
    except Exception as e:
        print(f"❌ LINE API連接失敗: {str(e)}")
        return False

def main():
    print("🚀 開始測試API連接...")
    print("="*50)
    
    # 從用戶輸入或程式碼中獲取參數
    print("請輸入你的API資訊：")
    print()
    
    openai_key = input("OpenAI API Key (sk-xxx): ").strip()
    if not openai_key:
        print("❌ 請提供OpenAI API Key")
        return
    
    line_token = input("LINE Access Token: ").strip()
    if not line_token:
        print("❌ 請提供LINE Access Token")
        return
    
    line_user_id = input("LINE User ID (Uxxx): ").strip()
    if not line_user_id:
        print("❌ 請提供LINE User ID")
        return
    
    print("\n" + "="*50)
    
    # 測試OpenAI
    openai_ok = test_openai_connection(openai_key)
    
    # 測試LINE
    line_ok = test_line_connection(line_token, line_user_id)
    
    print("\n" + "="*50)
    print("📋 測試結果摘要:")
    print(f"   OpenAI API: {'✅ 正常' if openai_ok else '❌ 失敗'}")
    print(f"   LINE API:   {'✅ 正常' if line_ok else '❌ 失敗'}")
    
    if openai_ok and line_ok:
        print("\n🎉 所有API測試通過！你可以開始使用新聞報告功能了")
        
        # 自動更新news_reporter.py中的參數
        try:
            with open("news_reporter.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            content = content.replace(
                'OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"',
                f'OPENAI_API_KEY = "{openai_key}"'
            )
            content = content.replace(
                'LINE_ACCESS_TOKEN = "YOUR_LINE_ACCESS_TOKEN_HERE"',
                f'LINE_ACCESS_TOKEN = "{line_token}"'
            )
            content = content.replace(
                'LINE_USER_ID = "YOUR_LINE_USER_ID_HERE"',
                f'LINE_USER_ID = "{line_user_id}"'
            )
            
            with open("news_reporter.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ news_reporter.py 已自動更新參數")
            print("\n▶️  執行以下命令開始生成新聞報告：")
            print("   python3 news_reporter.py")
            
        except Exception as e:
            print(f"⚠️  自動更新參數失敗: {str(e)}")
            print("   請手動編輯 news_reporter.py 填入參數")
    else:
        print("\n❌ 部分API測試失敗，請檢查設定後重新測試")

if __name__ == "__main__":
    main()