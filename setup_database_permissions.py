#!/usr/bin/env python3
from notion_client import Client
import json

def check_integration_access():
    """檢查Integration的存取狀況"""
    
    # 使用你的Integration Token
    NOTION_TOKEN = "ntn_u66191839913dbpwYTEPOBc5fwFXZtsw8VBumf1mniidYV"
    
    client = Client(auth=NOTION_TOKEN)
    
    try:
        print("🔍 檢查Integration存取權限...")
        
        # 搜尋所有可存取的內容
        results = client.search(filter={"property": "object", "value": "database"})
        
        print(f"📊 找到 {len(results['results'])} 個可存取的資料庫")
        
        if len(results['results']) > 0:
            print("\n✅ 可存取的資料庫：")
            for i, db in enumerate(results['results']):
                title = "無標題"
                if 'title' in db and db['title']:
                    title = db['title'][0]['text']['content'] if db['title'][0]['type'] == 'text' else '無標題'
                
                print(f"  {i+1}. {title}")
                print(f"     ID: {db['id']}")
                print(f"     URL: {db['url']}")
                
                # 如果找到包含 "Web3" 或 "Twitter" 的資料庫
                if "web3" in title.lower() or "twitter" in title.lower():
                    print(f"     ✅ 這可能是你的目標資料庫！")
                    return db['id'], db['url']
        
        # 嘗試搜尋所有頁面
        print("\n🔍 搜尋所有可存取的頁面...")
        all_results = client.search()
        
        print(f"📊 總共找到 {len(all_results['results'])} 個項目")
        
        for item in all_results['results']:
            if item['object'] == 'database':
                title = "無標題"
                if 'title' in item and item['title']:
                    title = item['title'][0]['text']['content'] if item['title'][0]['type'] == 'text' else '無標題'
                print(f"📋 資料庫: {title} (ID: {item['id']})")
            elif item['object'] == 'page':
                title = "無標題"
                if 'properties' in item and 'title' in item['properties']:
                    title_prop = item['properties']['title']
                    if 'title' in title_prop and title_prop['title']:
                        title = title_prop['title'][0]['text']['content']
                print(f"📄 頁面: {title} (ID: {item['id']})")
        
        return None, None
        
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {str(e)}")
        return None, None

def create_simple_test():
    """創建一個簡單的測試項目"""
    
    NOTION_TOKEN = "ntn_u66191839913dbpwYTEPOBc5fwFXZtsw8VBumf1mniidYV"
    client = Client(auth=NOTION_TOKEN)
    
    try:
        print("🧪 嘗試創建測試頁面...")
        
        # 嘗試在用戶的個人space中創建頁面
        page = client.pages.create(
            parent={"type": "page_id", "page_id": "root"},  # 根目錄
            properties={
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Notion Integration 測試頁面"
                        }
                    }
                ]
            }
        )
        
        print(f"✅ 成功創建測試頁面: {page['url']}")
        return True
        
    except Exception as e:
        print(f"❌ 創建測試頁面失敗: {str(e)}")
        return False

def main():
    print("🚀 開始檢查Notion Integration狀況...")
    print("="*60)
    
    # 檢查存取權限
    db_id, db_url = check_integration_access()
    
    if db_id:
        print(f"\n🎉 找到可用的資料庫！")
        print(f"📋 資料庫ID: {db_id}")
        print(f"🔗 資料庫URL: {db_url}")
        
        # 更新程式碼中的資料庫ID
        print("\n🔧 更新程式碼...")
        try:
            # 更新主程式
            with open("twitter_web3_crawler.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            old_id = "25c18a88bb77800292c9d48bb692906c"
            content = content.replace(old_id, db_id.replace("-", ""))
            
            with open("twitter_web3_crawler.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            print("✅ 主程式已更新")
            
        except Exception as e:
            print(f"⚠️  更新程式碼失敗: {str(e)}")
    
    else:
        print("\n❌ 無法找到可存取的資料庫")
        print("\n💡 建議：")
        print("1. 在Notion中手動創建一個新頁面")
        print("2. 在該頁面中添加 X_Web3News 為協作者")
        print("3. 然後在頁面中創建資料庫")
        
        # 嘗試創建測試頁面
        print("\n🧪 測試創建權限...")
        success = create_simple_test()
        
        if not success:
            print("\n🔧 可能的解決方案：")
            print("1. 檢查Integration設定中的workspace是否正確")
            print("2. 確認Integration有足夠的權限")
            print("3. 嘗試重新創建Integration")

if __name__ == "__main__":
    main()