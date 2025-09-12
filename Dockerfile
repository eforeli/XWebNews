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

# Replace any auto-generated test_apis.py with correct version
RUN cat > /test_apis.py << 'EOF'
import os, requests, tweepy, openai
print("🧪 Testing APIs...")
try:
    # Test Twitter
    client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))
    me = client.get_me()
    print("✅ Twitter API: OK")
except Exception as e:
    print(f"❌ Twitter API: {e}")
try:
    # Test OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":"hi"}], max_tokens=5)
    print("✅ OpenAI API: OK")
except Exception as e:
    print(f"❌ OpenAI API: {e}")
try:
    # Test LINE
    line_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_user_id = os.getenv("LINE_USER_ID")
    headers = {
        "Authorization": f"Bearer {line_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": line_user_id,
        "messages": [
            {"type": "text", "text": "🤖 XWebNews API Test - All systems operational!"}
        ]
    }
    r = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    if r.status_code == 200:
        print("✅ LINE API: OK - Test message sent!")
    else:
        print(f"❌ LINE API: {r.status_code} - {r.text}")
except Exception as e:
    print(f"❌ LINE API: {e}")
print("📋 API tests complete!")
EOF

# Create entrypoint that runs tests then starts scheduler
RUN echo '#!/bin/bash\necho "🚀 Starting XWebNews Crawler..."\npython3 /test_apis.py\necho "🔄 Starting cron service..."\npython3 scheduler.py' > /entrypoint.sh && chmod +x /entrypoint.sh

# Use entrypoint
CMD ["/entrypoint.sh"]