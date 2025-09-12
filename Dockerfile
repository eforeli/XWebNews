FROM python:3.11-slim

LABEL language=python

# 安裝系統依賴
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只複製絕對必要的檔案
COPY scheduler.py .
COPY rotational_crawler.py .
COPY news_reporter.py .

# 設置時區
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 設置 cron job
RUN echo "0 8 * * * cd /app && python3 rotational_crawler.py >> daily_crawl.log 2>&1" | crontab -

# 徹底清除任何測試檔案
RUN find /app -name "*test*" -type f -delete || true
RUN find / -name "*test_apis*" -type f -delete 2>/dev/null || true
RUN rm -f /test_apis.py /app/test_apis.py ./test_apis.py 2>/dev/null || true

# 創建最簡單的啟動腳本 - 不執行任何測試
RUN echo '#!/bin/bash\nset -e\necho "🚀 XWebNews Crawler Starting..."\necho "🔄 Starting cron..."\ncron\necho "📅 Starting scheduler directly..."\nexec python3 scheduler.py' > /start.sh && chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]