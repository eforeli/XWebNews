#!/usr/bin/env python3
"""
LINE User ID 獲取工具

使用方法：
1. 設定好你的LINE Channel Access Token
2. 執行這個腳本
3. 從你的LINE向Bot發送任何訊息
4. 腳本會顯示你的User ID
"""

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
import threading
import time

app = Flask(__name__)

# 設定參數 - 請填入你的實際值
LINE_ACCESS_TOKEN = "YOUR_LINE_ACCESS_TOKEN_HERE"
LINE_CHANNEL_SECRET = "YOUR_LINE_CHANNEL_SECRET_HERE"

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 儲存找到的User ID
found_user_ids = []

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    
    print(f"✅ 收到訊息！")
    print(f"   User ID: {user_id}")
    print(f"   訊息內容: {user_message}")
    
    # 儲存User ID
    if user_id not in found_user_ids:
        found_user_ids.append(user_id)
    
    # 回覆確認訊息
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f"🎉 User ID獲取成功！\n你的User ID是:\n{user_id}")
        )
    except Exception as e:
        print(f"回覆訊息失敗: {e}")

def run_simple_server():
    """執行簡單的webhook server"""
    print("🚀 啟動LINE Webhook服務...")
    print("⚠️  注意：這是本地測試用途，僅能處理基本功能")
    
    # 使用簡單的HTTP server
    import http.server
    import socketserver
    from urllib.parse import urlparse, parse_qs
    import json
    
    class LineWebhookHandler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/callback':
                # 讀取POST數據
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                try:
                    webhook_data = json.loads(post_data.decode('utf-8'))
                    
                    # 處理訊息事件
                    for event in webhook_data.get('events', []):
                        if event.get('type') == 'message':
                            user_id = event.get('source', {}).get('userId')
                            message_text = event.get('message', {}).get('text', '')
                            
                            if user_id:
                                print(f"✅ 收到訊息！")
                                print(f"   User ID: {user_id}")
                                print(f"   訊息內容: {message_text}")
                                
                                if user_id not in found_user_ids:
                                    found_user_ids.append(user_id)
                                
                                # 嘗試回覆訊息（需要reply token）
                                reply_token = event.get('replyToken')
                                if reply_token:
                                    try:
                                        line_bot_api.reply_message(
                                            reply_token,
                                            TextMessage(text=f"🎉 User ID獲取成功！\n你的User ID是:\n{user_id}")
                                        )
                                    except Exception as e:
                                        print(f"回覆訊息失敗: {e}")
                    
                    # 回應200 OK
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                    
                except Exception as e:
                    print(f"處理webhook數據時發生錯誤: {e}")
                    self.send_response(400)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # 抑制HTTP server的日誌輸出
            pass
    
    # 啟動服務器
    PORT = 8000
    with socketserver.TCPServer(("", PORT), LineWebhookHandler) as httpd:
        print(f"📡 Webhook服務器運行在: http://localhost:{PORT}")
        print("\n📋 接下來的步驟:")
        print("1. 使用ngrok或其他工具將localhost暴露到公網")
        print("2. 在LINE Developer Console設定Webhook URL")
        print("3. 從你的LINE向Bot發送任何訊息")
        print("4. 腳本會顯示你的User ID")
        print("\n按 Ctrl+C 停止服務")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服務已停止")

def alternative_method():
    """替代方法：使用LINE Bot API獲取User ID"""
    print("\n🔧 替代方法：手動獲取User ID")
    print("="*50)
    
    if (LINE_ACCESS_TOKEN == "YOUR_LINE_ACCESS_TOKEN_HERE" or 
        LINE_CHANNEL_SECRET == "YOUR_LINE_CHANNEL_SECRET_HERE"):
        print("❌ 請先在腳本中設定LINE_ACCESS_TOKEN和LINE_CHANNEL_SECRET")
        return
    
    print("請執行以下步驟：")
    print("1. 確保你已經加LINE Bot為好友")
    print("2. 向Bot發送任何一則訊息")
    print("3. 前往LINE Developer Console:")
    print("   - 打開你的Channel頁面")
    print("   - 點擊 'Messaging API' 標籤")
    print("   - 查看是否有 'User ID' 資訊顯示")
    print("\n如果以上方法都不行，請聯繫技術支援。")

def main():
    print("🔍 LINE User ID 獲取工具")
    print("="*50)
    
    print("選擇獲取方法：")
    print("1. 啟動Webhook服務器（需要ngrok）")
    print("2. 查看替代方法說明")
    print("3. 直接輸入已知的User ID進行測試")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        if (LINE_ACCESS_TOKEN == "YOUR_LINE_ACCESS_TOKEN_HERE" or 
            LINE_CHANNEL_SECRET == "YOUR_LINE_CHANNEL_SECRET_HERE"):
            print("❌ 請先編輯此腳本，填入你的LINE_ACCESS_TOKEN和LINE_CHANNEL_SECRET")
            return
        
        run_simple_server()
        
    elif choice == "2":
        alternative_method()
        
    elif choice == "3":
        user_id = input("請輸入你的User ID: ").strip()
        if user_id.startswith('U') and len(user_id) == 33:
            print(f"✅ User ID格式正確: {user_id}")
            
            # 嘗試發送測試訊息
            if LINE_ACCESS_TOKEN != "YOUR_LINE_ACCESS_TOKEN_HERE":
                try:
                    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
                    line_bot_api.push_message(
                        user_id,
                        TextMessage(text="🧪 User ID測試訊息 - 收到表示設定正確！")
                    )
                    print("✅ 測試訊息已發送")
                except Exception as e:
                    print(f"❌ 發送測試訊息失敗: {e}")
            
            found_user_ids.append(user_id)
        else:
            print("❌ User ID格式不正確，應該是 U 開頭的33位字符")
    
    else:
        print("❌ 無效選擇")
        return
    
    # 顯示結果
    if found_user_ids:
        print("\n🎉 找到的User ID：")
        for user_id in found_user_ids:
            print(f"   {user_id}")
        
        print("\n📝 請將此User ID複製到news_reporter.py中：")
        print(f'LINE_USER_ID = "{found_user_ids[0]}"')

if __name__ == "__main__":
    main()