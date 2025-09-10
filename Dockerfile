FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ONLY the three essential files - nothing else
COPY scheduler.py .
COPY rotational_crawler.py .
COPY news_reporter.py .

# Set timezone
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Fix any auto-generated test_apis.py with syntax errors
RUN if [ -f /test_apis.py ]; then \
    sed -i 's/os\.getenv(\\"LINE_CHANNEL_ACCESS_TOKEN\\")/os.getenv("LINE_CHANNEL_ACCESS_TOKEN")/g' /test_apis.py; \
    fi

# Create entrypoint that skips problematic test files
RUN echo '#!/bin/bash\necho "🚀 Starting XWebNews Crawler..."\npython3 scheduler.py' > /entrypoint.sh && chmod +x /entrypoint.sh

# Use entrypoint to avoid any test execution
CMD ["/entrypoint.sh"]