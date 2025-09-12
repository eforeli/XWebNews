#!/usr/bin/env python3
import os
import requests
import tweepy
import openai

print("🧪 Testing APIs...")

try:
    # Test Twitter
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    client = tweepy.Client(bearer_token=bearer_token)
    me = client.get_me()
    print("✅ Twitter API: OK")
except Exception as e:
    print(f"❌ Twitter API: {e}")

try:
    # Test OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role":"user","content":"hi"}], 
        max_tokens=5
    )
    print("✅ OpenAI API: OK")
except Exception as e:
    print(f"❌ OpenAI API: {e}")

try:
    # Test LINE - FIXED SYNTAX
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