#!/usr/bin/env python3
import json
import openai
import requests
import os
from datetime import datetime
from typing import Dict, List, Any
import logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Web3NewsReporter:
    def __init__(self, openai_api_key: str, line_access_token: str, line_user_id: str):
        """
        初始化Web3新聞報告器
        
        Args:
            openai_api_key: OpenAI API Key
            line_access_token: LINE Channel Access Token
            line_user_id: 接收推播的LINE User ID
        """
        # OpenAI設定
        openai.api_key = openai_api_key
        
        # LINE設定
        self.line_access_token = line_access_token
        self.line_user_id = line_user_id
        self.line_api_url = "https://api.line.me/v2/bot/message/push"
        
        self.setup_logging()
    
    def setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('news_reporter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_latest_tweets(self) -> Dict[str, List[Dict[str, Any]]]:
        """載入最新的推文數據"""
        import glob
        import os
        
        try:
            # 尋找最新的JSON數據文件
            json_files = glob.glob("web3_tweets_*.json")
            if not json_files:
                self.logger.error("找不到推文數據文件")
                return {}
            
            latest_file = max(json_files, key=os.path.getctime)
            self.logger.info(f"載入數據文件: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"載入推文數據時發生錯誤: {str(e)}")
            return {}

    def analyze_tweets_with_openai(self, tweets_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        使用OpenAI分析推文並生成新聞報告
        
        Args:
            tweets_data: 推文數據
            
        Returns:
            str: 生成的新聞報告
        """
        try:
            # 準備數據供AI分析
            analysis_text = self.prepare_analysis_data(tweets_data)
            
            if not analysis_text:
                return "今日暫無Web3相關推文數據。"
            
            # 建立OpenAI prompt
            prompt = self.create_analysis_prompt(analysis_text)
            
            # 調用OpenAI API
            self.logger.info("正在使用OpenAI分析推文內容...")
            # 嘗試使用最便宜的模型，如果失敗則回退
            models_to_try = ["gpt-4o-mini", "gpt-3.5-turbo"]
            
            for model in models_to_try:
                try:
                    self.logger.info(f"嘗試使用模型: {model}")
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "你是一位專業的Web3新聞分析師，專門為繁體中文用戶提供準確、簡潔的加密貨幣和區塊鏈新聞摘要。"
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=1500,
                        temperature=0.7
                    )
                    
                    report = response.choices[0].message.content.strip()
                    self.logger.info(f"✅ {model} 分析完成")
                    return report
                    
                except Exception as model_error:
                    self.logger.warning(f"模型 {model} 失敗: {str(model_error)}")
                    if model == models_to_try[-1]:  # 最後一個模型也失敗
                        raise model_error
                    continue
            
        except Exception as e:
            self.logger.error(f"OpenAI分析時發生錯誤: {str(e)}")
            return f"分析過程中發生錯誤: {str(e)}"

    def prepare_analysis_data(self, tweets_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """準備供AI分析的數據"""
        analysis_parts = []
        total_tweets = 0
        
        for category, tweets in tweets_data.items():
            if not tweets:
                continue
                
            # 按讚數排序，取前10條
            sorted_tweets = sorted(tweets, key=lambda x: x.get('like_count', 0), reverse=True)[:10]
            total_tweets += len(sorted_tweets)
            
            category_text = f"\n=== {category} 類別 ===\n"
            for i, tweet in enumerate(sorted_tweets, 1):
                tweet_info = (
                    f"{i}. 【{tweet.get('username', 'unknown')}】\n"
                    f"   內容: {tweet.get('text', '')[:200]}...\n"
                    f"   互動: ❤️{tweet.get('like_count', 0)} 🔄{tweet.get('retweet_count', 0)}\n"
                    f"   時間: {tweet.get('created_at', 'unknown')}\n"
                )
                category_text += tweet_info
            
            analysis_parts.append(category_text)
        
        if total_tweets == 0:
            return ""
        
        header = f"今日Web3推文分析數據 ({total_tweets}條推文):\n"
        return header + "\n".join(analysis_parts)

    def create_analysis_prompt(self, data: str) -> str:
        """創建OpenAI分析提示"""
        today = datetime.now().strftime("%Y年%m月%d日")
        
        prompt = f"""
請根據以下{today}的Web3推文數據，生成一份簡潔的新聞報告：

{data}

請按以下格式整理：

📅 **{today} Web3 市場動態**

🔥 **今日熱點**
- [列出2-3個最重要的趨勢或事件]

📊 **各賽道觀察**
- **DeFi**: [重點摘要]
- **NFT/GameFi**: [重點摘要] 
- **Layer1/2**: [重點摘要]
- **其他**: [重點摘要]

💡 **市場洞察**
- [基於數據的1-2點深度觀察]

⚠️ **風險提醒**
僅供參考，投資有風險，請自行判斷。

要求：
1. 內容要簡潔，總字數控制在500字內
2. 重點突出，條理清晰
3. 使用繁體中文
4. 客觀中性，避免投資建議
5. 如果某個賽道沒有重要動態，可以省略
"""
        return prompt

    def send_to_line(self, message: str) -> bool:
        """
        發送消息到LINE
        
        Args:
            message: 要發送的消息內容
            
        Returns:
            bool: 發送是否成功
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.line_access_token}',
                'Content-Type': 'application/json'
            }
            
            # LINE訊息格式
            data = {
                'to': self.line_user_id,
                'messages': [
                    {
                        'type': 'text',
                        'text': message
                    }
                ]
            }
            
            self.logger.info("正在發送訊息到LINE...")
            response = requests.post(
                self.line_api_url, 
                headers=headers, 
                json=data
            )
            
            if response.status_code == 200:
                self.logger.info("✅ LINE訊息發送成功")
                return True
            else:
                self.logger.error(f"❌ LINE訊息發送失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"發送LINE訊息時發生錯誤: {str(e)}")
            return False

    def generate_and_send_report(self) -> bool:
        """生成新聞報告並發送到LINE"""
        try:
            self.logger.info("開始生成Web3新聞報告...")
            
            # 1. 載入最新推文數據
            tweets_data = self.load_latest_tweets()
            if not tweets_data:
                self.logger.error("無法載入推文數據")
                return False
            
            # 2. 使用OpenAI分析生成報告
            report = self.analyze_tweets_with_openai(tweets_data)
            if not report or "錯誤" in report:
                self.logger.error("報告生成失敗")
                return False
            
            # 3. 保存報告到文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"web3_news_report_{timestamp}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"報告已保存到: {report_filename}")
            
            # 4. 發送到LINE
            success = self.send_to_line(report)
            
            if success:
                self.logger.info("🎉 Web3新聞報告生成並發送完成！")
                return True
            else:
                self.logger.error("報告生成成功，但LINE發送失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"生成報告過程中發生錯誤: {str(e)}")
            return False

def main():
    # 設定參數
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    LINE_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'your_line_channel_access_token_here')
    LINE_USER_ID = os.getenv('LINE_USER_ID', 'your_line_user_id_here')
    
    # 檢查參數設定
    if (OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE" or 
        LINE_ACCESS_TOKEN == "YOUR_LINE_ACCESS_TOKEN_HERE" or
        LINE_USER_ID == "YOUR_LINE_USER_ID_HERE"):
        
        print("請先設定API金鑰和LINE參數：")
        print("1. OPENAI_API_KEY - OpenAI API 金鑰")
        print("2. LINE_ACCESS_TOKEN - LINE Channel Access Token")
        print("3. LINE_USER_ID - 你的LINE User ID")
        return
    
    # 創建新聞報告器
    reporter = Web3NewsReporter(
        openai_api_key=OPENAI_API_KEY,
        line_access_token=LINE_ACCESS_TOKEN,
        line_user_id=LINE_USER_ID
    )
    
    # 生成並發送報告
    success = reporter.generate_and_send_report()
    
    if success:
        print("✅ 新聞報告已成功生成並發送到LINE")
    else:
        print("❌ 新聞報告生成或發送失敗，請檢查日誌")

if __name__ == "__main__":
    main()