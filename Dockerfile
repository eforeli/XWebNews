FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Set timezone and cron job for daily execution at 8 AM Taiwan time (UTC+8 = 0 AM UTC)
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "0 8 * * * cd /app && python3 rotational_crawler.py >> daily_crawl.log 2>&1" | crontab -

# Create entrypoint script
RUN echo '#!/bin/bash\n\
cron\n\
tail -f /dev/null' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8080

CMD ["/entrypoint.sh"]