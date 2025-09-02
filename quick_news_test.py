#!/usr/bin/env python3
"""
快速新聞測試 - 使用現有數據生成報告
"""

import json
import openai
import requests
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def quick_test():
    print("🚀 快速測試Web3新聞生成...")
    
    # API設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'your_line_channel_access_token_here')
    LINE_USER_ID = os.getenv('LINE_USER_ID', 'your_line_user_id_here')
    
    # 載入最新數據
    import glob
    import os
    json_files = glob.glob("*web3_tweets*.json")
    if not json_files:
        print("❌ 找不到推文數據")
        return False
    
    latest_file = max(json_files, key=os.path.getctime)
    print(f"📊 使用數據: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
    
    total_tweets = sum(len(tweets) for tweets in tweets_data.values())
    print(f"📈 分析 {total_tweets} 條推文...")
    
    # 準備AI分析數據
    analysis_text = f"今日Web3推文分析數據 ({total_tweets}條推文):\n\n"
    
    for category, tweets in tweets_data.items():
        if tweets:
            # 取前5條最高互動度推文
            sorted_tweets = sorted(tweets, key=lambda x: x.get('like_count', 0) + x.get('retweet_count', 0), reverse=True)[:5]
            analysis_text += f"\n=== {category} 類別 ===\n"
            for i, tweet in enumerate(sorted_tweets, 1):
                analysis_text += f"{i}. 【{tweet.get('username', 'unknown')}】\n"
                analysis_text += f"   內容: {tweet.get('text', '')[:150]}...\n"
                analysis_text += f"   互動: ❤️{tweet.get('like_count', 0)} 🔄{tweet.get('retweet_count', 0)}\n\n"
    
    # AI分析
    openai.api_key = OPENAI_API_KEY
    
    prompt = f"""
請根據以下Web3推文數據，生成一份簡潔的新聞報告：

{analysis_text[:3000]}  # 限制長度

請按以下格式整理：

📅 **今日 Web3 精選動態**

🔥 **今日熱點**
- [列出2-3個最重要的趨勢或事件]

📊 **各賽道觀察** 
- **DeFi**: [重點摘要]
- **Layer1/2**: [重點摘要]
- **其他**: [如有重要動態]

💡 **市場洞察**
- [1-2點基於數據的觀察]

⚠️ **風險提醒**
僅供參考，投資有風險，請自行判斷。

要求：
1. 內容簡潔，總字數400字內
2. 重點突出，條理清晰  
3. 使用繁體中文
4. 客觀中性
"""
    
    print("🤖 正在生成AI新聞報告...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是專業的Web3新聞分析師，為繁體中文用戶提供準確簡潔的加密貨幣新聞摘要。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        report = response.choices[0].message.content.strip()
        print("✅ AI報告生成成功")
        
    except Exception as e:
        print(f"❌ AI分析失敗: {str(e)}")
        # 使用簡化版報告
        report = f"""📅 **今日 Web3 精選動態**

🔥 **數據摘要**
- 成功分析 {total_tweets} 條精選Web3推文
- 涵蓋 {len([k for k,v in tweets_data.items() if v])} 個主要賽道

📊 **主要類別**
{chr(10).join([f"- **{k}**: {len(v)} 條推文" for k,v in tweets_data.items() if v])}

💡 **系統提醒**
由於API限制，本次使用基礎分析。數據已保存供後續詳細分析。

⚠️ **風險提醒**
僅供參考，投資有風險，請自行判斷。"""
    
    # 保存報告
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"quick_news_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 報告已保存: {report_file}")
    
    # 發送到LINE
    print("📱 發送到LINE...")
    try:
        headers = {
            'Authorization': f'Bearer {LINE_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        enhanced_report = f"📊 Web3精選 ({total_tweets}條推文)\n{'='*30}\n\n{report}"
        
        data = {
            'to': LINE_USER_ID,
            'messages': [{'type': 'text', 'text': enhanced_report}]
        }
        
        response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
        
        if response.status_code == 200:
            print("✅ LINE推送成功")
            return True
        else:
            print(f"❌ LINE推送失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ LINE推送錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 快速新聞測試成功！")
        print("📱 請檢查你的LINE")
    else:
        print("\n⚠️ 測試部分成功，請檢查報告文件")