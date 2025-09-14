FROM python:3.11-slim

# 明確告訴 Zeabur 這是 Python 專案
LABEL language=python
LABEL version="2025-09-14-force-rebuild"

WORKDIR /app

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製必要的運行檔案
COPY scheduler.py .
COPY rotational_crawler.py .
COPY news_reporter.py .
COPY test_apis.py .

# 創建正確結構的狀態文件
RUN echo '{"rotation_index": 0, "last_crawled": {}}' > crawler_rotation_state.json

# 設置時區
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 創建啟動腳本，先測試 API 再運行排程器
RUN echo '#!/bin/bash\necho "🚀 Starting XWebNews Crawler..."\npython3 test_apis.py\necho "📅 Python scheduler starting..."\npython3 scheduler.py' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]