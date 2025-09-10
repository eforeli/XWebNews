FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (excluding problematic test files)
COPY *.py ./
COPY *.json ./
COPY *.txt ./
COPY .env* ./

# Set timezone
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Verify Python syntax before starting
RUN python3 -m py_compile scheduler.py
RUN python3 -m py_compile rotational_crawler.py
RUN python3 -m py_compile news_reporter.py

EXPOSE 8080

# Use Python scheduler instead of cron
CMD ["python3", "scheduler.py"]