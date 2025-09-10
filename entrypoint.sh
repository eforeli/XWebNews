#!/bin/bash

echo "🚀 Starting XWebNews Crawler..."

# 檢查必要檔案是否存在
if [ ! -f "scheduler.py" ]; then
    echo "❌ scheduler.py not found"
    exit 1
fi

if [ ! -f "rotational_crawler.py" ]; then
    echo "❌ rotational_crawler.py not found"
    exit 1
fi

if [ ! -f "news_reporter.py" ]; then
    echo "❌ news_reporter.py not found"
    exit 1
fi

# 驗證 Python 語法
echo "🔍 Validating Python syntax..."
python3 -m py_compile scheduler.py || exit 1
python3 -m py_compile rotational_crawler.py || exit 1
python3 -m py_compile news_reporter.py || exit 1

echo "✅ All syntax checks passed"

# 啟動排程器
echo "📅 Starting scheduler..."
python3 scheduler.py