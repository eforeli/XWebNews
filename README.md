# Web3 Twitter 爬蟲與智能新聞系統

一個完整的Web3資訊自動化解決方案：Twitter數據爬取 → OpenAI智能分析 → LINE新聞推播

## 🎯 核心功能

### 1. Twitter數據爬取
- 🔍 **多賽道監控**: 支援DeFi、Layer1/2、NFT/GameFi、AI+Crypto、RWA、Meme Coins、基礎設施等7大Web3賽道
- 📊 **智能分析**: 自動分析熱門關鍵字、互動度趨勢、認證用戶比例等
- 💾 **多格式輸出**: 支援JSON、CSV格式保存數據
- 🚀 **合規安全**: 使用官方Twitter API v2，完全合法合規

### 2. AI新聞報告生成
- 🤖 **OpenAI GPT-4分析**: 智能整理推文內容，生成專業新聞報告
- 📝 **中文報告**: 針對繁體中文用戶優化，提供易讀的市場動態分析
- 💡 **深度洞察**: 基於數據提供市場趨勢分析和風險提醒
- 📊 **分類整理**: 按賽道分組，突出重點事件和趨勢

### 3. LINE自動推播
- 📱 **即時推送**: 自動將新聞報告推送到您的LINE
- ⏰ **定時執行**: 支援每日定時自動生成和推播
- 🎨 **格式化訊息**: 清晰的排版，適合手機閱讀

## 監控的Web3賽道

### 1. DeFi (去中心化金融)
關鍵字: DeFi, DEX, liquidity, yield farming, staking, AMM, lending protocol, UniSwap, SushiSwap, Compound

### 2. Layer1/Layer2
關鍵字: Ethereum, Bitcoin, Solana, Polygon, Arbitrum, Optimism, scaling, Layer2, rollup

### 3. NFT & GameFi
關鍵字: NFT, GameFi, P2E, metaverse, gaming, collectibles, OpenSea, play to earn

### 4. AI + Crypto
關鍵字: AI crypto, machine learning, artificial intelligence blockchain, AI token, GPT, neural network crypto

### 5. RWA (真實世界資產)
關鍵字: RWA, tokenization, real world assets, commodity, real estate token, asset backed

### 6. Meme Coins
關鍵字: meme coin, DOGE, SHIB, community token, dogecoin, shiba inu

### 7. 基礎設施
關鍵字: Web3 infrastructure, oracle, cross-chain, bridge, Chainlink, interoperability

## 安裝與設置

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 獲取Twitter API認證
1. 前往 [Twitter Developer Portal](https://developer.twitter.com)
2. 申請開發者帳戶
3. 創建新的App
4. 獲取 Bearer Token

### 3. 設置環境變數
複製 `.env.example` 為 `.env` 並填入你的API密鑰:
```bash
cp .env.example .env
```

編輯 `.env` 文件:
```
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

## 使用方法

### 🚀 快速開始：完整自動化流程
```bash
# 一鍵執行：爬蟲 → AI分析 → LINE推播
python3 daily_web3_news.py
```

### 📋 分步驟執行

#### 1. 僅執行Twitter爬蟲
```bash
python3 twitter_web3_crawler.py
```
- 爬取各個Web3賽道的最新推文
- 保存數據到JSON和CSV文件
- 生成基本的分析報告

#### 2. 僅生成AI新聞報告
```bash
python3 news_reporter.py
```
- 使用OpenAI分析推文數據
- 生成專業新聞報告
- 自動推送到LINE

#### 3. 數據視覺化分析
```bash
python3 web3_analyzer.py
```
- 生成詳細的趨勢報告
- 創建視覺化圖表
- 找出熱門關鍵字

### 🔧 API測試和設定
```bash
# 測試API連接並自動設定參數
python3 test_apis.py

# 獲取LINE User ID (如需要)
python3 get_line_user_id.py
```

## 輸出文件說明

- `web3_tweets_YYYYMMDD_HHMMSS.json` - 原始推文數據（JSON格式）
- `web3_tweets_YYYYMMDD_HHMMSS.csv` - 推文數據（CSV格式）
- `web3_analysis.json` - 分析結果
- `web3_summary_report.txt` - 詳細分析報告
- `web3_analysis_plots.png` - 數據視覺化圖表
- `twitter_crawler.log` - 執行日誌

## API使用限制

### 免費版限制
- 每月 10,000 條推文
- 每15分鐘 450 次請求
- 只能搜尋過去7天的推文

### 付費版特色
- 更高的API配額
- 歷史數據存取
- 更多數據欄位

## 自定義設置

### 修改關鍵字
編輯 `twitter_web3_crawler.py` 中的 `web3_categories` 字典：

```python
self.web3_categories = {
    "Your_Category": ["keyword1", "keyword2", "keyword3"],
    # 添加更多類別...
}
```

### 調整爬取數量
修改 `main()` 函數中的參數：

```python
all_tweets = crawler.crawl_all_categories(tweets_per_category=100)  # 調整數量
```

## 注意事項

- 確保遵守Twitter的服務條款
- 避免過於頻繁的API請求
- 定期檢查API配額使用情況
- 保護好你的API密鑰，不要提交到版本控制系統

## 故障排除

### 常見錯誤

1. **認證失敗**
   - 檢查Bearer Token是否正確
   - 確認API密鑰沒有過期

2. **API配額耗盡**
   - 檢查當月使用量
   - 考慮升級到付費計劃

3. **數據為空**
   - 檢查關鍵字是否過於特殊
   - 確認時間範圍內有相關推文

## 貢獻

歡迎提交Issue和Pull Request來改進這個工具！

## 🔑 API設定需求

### 必需的API金鑰
1. **Twitter Bearer Token** - 已設定 ✅
2. **OpenAI API Key** - 需要你提供
3. **LINE Channel Access Token** - 需要你提供
4. **LINE User ID** - 需要你提供

### 📋 設定步驟總覽
1. **OpenAI**: 前往 [platform.openai.com](https://platform.openai.com) 註冊並獲取API Key
2. **LINE**: 前往 [developers.line.biz](https://developers.line.biz) 創建Messaging API Channel
3. **執行設定**: `python3 test_apis.py` 自動測試和配置

詳細設定說明請參考：`setup_line_openai.md`

## 💰 費用說明
- **Twitter API**: 免費版（已設定）
- **OpenAI**: 使用最便宜的GPT-4o-mini模型，每份報告約 $0.002
- **LINE API**: 完全免費

## 📅 自動化執行
```bash
# 設定每日定時執行（macOS/Linux）
crontab -e

# 每天上午9點自動生成新聞
0 9 * * * cd "/Users/eli/Documents/CC camp/web crawler" && python3 daily_web3_news.py
```

## 🛠️ 故障排除
詳細的故障排除指南請參考：
- `setup_line_openai.md` - API設定問題
- `*.log` 文件 - 執行日誌
- `python3 test_apis.py` - 連接測試

## 授權

MIT License