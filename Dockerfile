FROM python:3.11-slim

LABEL language=python

# 安裝系統依賴
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 設置時區
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 設置 cron job
RUN echo "0 8 * * * cd /app && python3 rotational_crawler.py >> daily_crawl.log 2>&1" | crontab -

# 創建啟動腳本（專門針對我們的 scheduler.py）
RUN echo '#!/bin/bash\necho "🚀 Starting XWebNews Crawler..."\necho "🔄 Starting cron service..."\ncron\n\n# 啟動我們的 Python 排程器\nif [ -f "scheduler.py" ]; then\n    python3 scheduler.py\nelse\n    # 備用：直接執行爬蟲\n    python3 rotational_crawler.py\nfi' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]