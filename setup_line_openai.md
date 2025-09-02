# LINE推播 & OpenAI 新聞報告設定指南

## 第一部分：OpenAI API 設定

### 1. 註冊OpenAI帳戶
1. 前往 [platform.openai.com](https://platform.openai.com)
2. 註冊或登入帳戶
3. 完成手機驗證

### 2. 獲取API Key
1. 點擊右上角頭像 → "View API keys"
2. 點擊 "Create new secret key"
3. 複製API Key（格式：`sk-xxxxxxxxxxxxxxxx`）
4. ⚠️ **重要**：API Key只會顯示一次，請妥善保存

### 3. 充值帳戶（必需）
1. 前往 "Billing" → "Payment methods"
2. 添加信用卡並充值（建議最低$5-10）
3. OpenAI是按使用量付費，GPT-4大約每1000 tokens $0.03

---

## 第二部分：LINE Developer 設定

### 1. 創建LINE Developer帳戶
1. 前往 [developers.line.biz](https://developers.line.biz/console)
2. 用你的LINE帳戶登入
3. 創建新的 Provider（公司/個人名稱）

### 2. 創建Messaging API Channel
1. 在Provider下點擊 "Create a Messaging API channel"
2. 填寫以下資訊：
   - **Channel name**: `Web3 News Bot`
   - **Channel description**: `個人Web3新聞推播機器人`
   - **Category**: `News`
   - **Subcategory**: `IT/Technology`

### 3. 取得重要資訊
創建成功後，前往Channel設定頁面：

#### 3.1 Channel Access Token
1. 點擊 "Messaging API" 標籤
2. 往下滑到 "Channel access token"
3. 點擊 "Issue" 生成Token
4. 複製Token（格式很長：`xxxxxxxxxxxxx...`）

#### 3.2 Channel Secret
1. 在 "Basic settings" 標籤中
2. 找到 "Channel secret"
3. 點擊顯示並複製

### 4. 加Bot為好友並取得User ID
1. 在Channel頁面找到QR Code，用LINE掃描加Bot為好友
2. 或者點擊Bot的LINE URL直接加好友

#### 取得你的User ID：
**方法1：使用Webhook（推薦）**
```python
# 執行以下測試程式獲取User ID
python3 get_line_user_id.py
```

**方法2：LINE Developer Console**
- 有些情況下會在Channel頁面顯示
- 格式：`Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 第三部分：程式設定

### 1. 安裝相依套件
```bash
pip3 install -r requirements.txt
```

### 2. 填入API參數
編輯 `news_reporter.py` 檔案中的以下參數：

```python
# 第xxx行左右
OPENAI_API_KEY = "sk-你的OpenAI API Key"
LINE_ACCESS_TOKEN = "你的LINE Channel Access Token"  
LINE_USER_ID = "你的LINE User ID"
```

### 3. 測試設定
```bash
# 測試各項API連接
python3 test_apis.py

# 執行完整流程
python3 news_reporter.py
```

---

## 第四部分：自動化執行

### 設定定時執行（macOS/Linux）
```bash
# 編輯crontab
crontab -e

# 添加以下行（每天早上9點執行）
0 9 * * * cd "/Users/eli/Documents/CC camp/web crawler" && python3 news_reporter.py

# 或每天晚上8點執行
0 20 * * * cd "/Users/eli/Documents/CC camp/web crawler" && python3 news_reporter.py
```

---

## 💰 費用預估

### OpenAI費用
- **GPT-4**: ~$0.03/1000 tokens
- **每份報告**: 約1500 tokens = ~$0.045
- **每月30份報告**: 約$1.35

### LINE費用
- Messaging API：**完全免費**
- 每月可發送500則免費訊息

---

## 🔧 故障排除

### OpenAI相關
- **401 Unauthorized**: API Key錯誤或未設定
- **429 Rate Limit**: 請求太頻繁，稍等再試
- **402 Insufficient Credit**: 帳戶餘額不足，需要充值

### LINE相關
- **401 Unauthorized**: Channel Access Token錯誤
- **400 Bad Request**: User ID格式錯誤或用戶已封鎖Bot

### 一般問題
- **ImportError**: 執行 `pip3 install -r requirements.txt`
- **FileNotFoundError**: 確保先執行Twitter爬蟲生成數據文件

---

## 📝 需要提供的資料摘要

請提供以下三個資料給我：

1. **OpenAI API Key**: `sk-xxxxxxxxxxxxxxxx`
2. **LINE Channel Access Token**: `很長的token字串`
3. **你的LINE User ID**: `Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

提供這些資料後，我會立即幫你更新程式碼！