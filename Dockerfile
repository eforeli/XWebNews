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

# Start scheduler directly - no scripts, no tests
CMD ["python3", "scheduler.py"]