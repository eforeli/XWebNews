FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only essential files (exclude ALL test files)
COPY scheduler.py ./
COPY rotational_crawler.py ./
COPY news_reporter.py ./
COPY entrypoint.sh ./
COPY *.json ./
COPY .env* ./

# Set timezone
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8080

# Use entrypoint script with validation
CMD ["./entrypoint.sh"]