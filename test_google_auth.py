#!/usr/bin/env python3
"""
Test script to debug Google OAuth issues
"""
import os
import sys
sys.path.append('backend')

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import requests

# Load environment variables
from dotenv import load_dotenv
load_dotenv('backend/.env')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')

print(f"🔍 Testing Google OAuth Configuration")
print(f"📋 Client ID: {GOOGLE_CLIENT_ID}")
print(f"🌐 Environment: Local Development")
print("-" * 50)

# Test 1: Check if Google Client ID is loaded
if not GOOGLE_CLIENT_ID or GOOGLE_CLIENT_ID == '1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com':
    print("❌ Google Client ID not properly configured")
    print("   Check your backend/.env file")
else:
    print("✅ Google Client ID loaded successfully")

# Test 2: Test Google API connectivity
try:
    response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=invalid_token')
    if response.status_code == 400:
        print("✅ Google OAuth API is accessible")
        print(f"   Response: {response.json()}")
    else:
        print(f"⚠️  Unexpected response from Google API: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot reach Google OAuth API: {e}")

print("\n🔧 Common Issues and Solutions:")
print("1. Check Google Cloud Console configuration")
print("2. Verify authorized JavaScript origins include http://localhost:3000")
print("3. Ensure authorized redirect URIs are configured")
print("4. Make sure the Google OAuth consent screen is configured")
print("5. Check if your Google project has the necessary APIs enabled")

print("\n📝 Next Steps:")
print("1. Go to https://console.cloud.google.com/")
print("2. Select your project")
print("3. Go to APIs & Services → Credentials")
print("4. Edit your OAuth 2.0 Client ID")
print("5. Add http://localhost:3000 to authorized origins")
