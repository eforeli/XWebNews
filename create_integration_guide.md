# 創建Notion Integration詳細指南

## 步驟1: 前往Integration頁面
打開：https://www.notion.com/my-integrations

## 步驟2: 創建新的Integration
1. 點擊 **"+ New integration"**
2. 填寫以下信息：
   - **Name**: `Web3TwitterCrawler` (不要有空格)
   - **Associated workspace**: 選擇 "Eli" (你的個人workspace)
   - **Type**: 選擇 "Internal integration"

## 步驟3: 設定權限 (Capabilities)
確保以下權限都被勾選：
- ✅ **Read content**
- ✅ **Update content** 
- ✅ **Insert content**

## 步驟4: 提交創建
點擊 **"Submit"**

## 步驟5: 複製Integration Token
創建成功後，你會看到：
- **Internal Integration Token**: `secret_xxxxxxxxxx`
- 複製這個Token

## 步驟6: 測試新的Integration
創建完成後，新的Integration應該會出現在你的Connections列表中。

## 預期結果
完成後，在Settings > Connections頁面應該會看到：
- Web3TwitterCrawler (INTERNAL)

## 如果仍然有問題
1. 確認workspace選擇正確
2. 檢查是否有管理員權限
3. 嘗試刷新頁面或重新登入