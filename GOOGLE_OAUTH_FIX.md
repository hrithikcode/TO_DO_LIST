# 🔧 Fix Google OAuth "Authorization Error" - Complete Guide

## ❌ **The Error You're Seeing:**
```
Access blocked: Authorization Error
shwetay1508@gmail.com
The OAuth client was not found.
Error 401: invalid_client
```

## 🎯 **Root Cause:**
The app is using placeholder Google Client ID values instead of real Google OAuth credentials from Google Cloud Console.

## ✅ **Solution: Set Up Real Google OAuth Credentials**

### **Step 1: Create Google OAuth App**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create or Select Project:**
   - Click "Select a project" → "New Project"
   - Name: "Todo App OAuth" (or any name)
   - Click "Create"

3. **Enable Required APIs:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" or "Google Identity API"
   - Click "Enable"

4. **Configure OAuth Consent Screen:**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" (for testing with any Google account)
   - Fill required fields:
     - App name: "Todo App"
     - User support email: your email
     - Developer contact: your email
   - Click "Save and Continue"
   - Skip "Scopes" and "Test users" for now
   - Click "Back to Dashboard"

5. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "Todo App Web Client"
   - **Authorized JavaScript origins:**
     - `http://localhost:3000`
     - `http://127.0.0.1:3000`
   - **Authorized redirect URIs:**
     - `http://localhost:3000`
     - `http://127.0.0.1:3000`
   - Click "Create"

6. **Copy Credentials:**
   - Copy the "Client ID" (ends with .apps.googleusercontent.com)
   - Copy the "Client Secret"

### **Step 2: Configure the Todo App**

#### **Option A: Use the Setup Script (Recommended)**

```bash
# Navigate to the Todo app directory
cd ~/workspace/TO-DO_LIST

# Run the setup script
python3 setup_google_oauth.py
```

The script will ask for your Google Client ID and Client Secret, then automatically configure both backend and frontend.

#### **Option B: Manual Configuration**

1. **Create Backend Environment File:**
```bash
# Create backend/.env file
cat > backend/.env << EOF
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
EOF
```

2. **Create Frontend Environment File:**
```bash
# Create frontend/.env file
cat > frontend/.env << EOF
# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com

# API Configuration
REACT_APP_API_URL=http://localhost:5000

# Other Configuration
GENERATE_SOURCEMAP=false
EOF
```

### **Step 3: Restart the Application**

```bash
# Restart backend
cd ~/workspace/TO-DO_LIST/backend
pkill -f "python app.py"
python app.py &

# Restart frontend
cd ~/workspace/TO-DO_LIST/frontend
pkill -f "react-scripts"
npm start &
```

### **Step 4: Test Google OAuth**

1. **Open the app:** http://localhost:3000
2. **Click "Sign in with Google"**
3. **You should see:** Google's official login popup
4. **Login with:** Any Google account (including shwetay1508@gmail.com)
5. **Success:** You'll be logged into the Todo app

## 🚀 **Current Status (Before Fix):**

The app currently shows a "Configure Google OAuth" button instead of the real Google login button. This is intentional to prevent the error you encountered.

## ✅ **After Fix:**

- ✅ Real Google "Sign in with Google" button
- ✅ Official Google login popup
- ✅ Successful authentication with any Google account
- ✅ Profile picture from Google account
- ✅ Automatic username generation

## 🔍 **Troubleshooting:**

### **Common Issues:**

1. **"redirect_uri_mismatch"**
   - **Fix:** Add `http://localhost:3000` to authorized redirect URIs in Google Console

2. **"origin_mismatch"**
   - **Fix:** Add `http://localhost:3000` to authorized JavaScript origins

3. **"invalid_client"**
   - **Fix:** Double-check Client ID is correct in both .env files

4. **"access_denied"**
   - **Fix:** Make sure OAuth consent screen is configured

### **Verification Steps:**

```bash
# Check if environment variables are loaded
cd ~/workspace/TO-DO_LIST/backend
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Google Client ID:', os.getenv('GOOGLE_CLIENT_ID', 'Not found'))
print('Client ID valid:', 'apps.googleusercontent.com' in str(os.getenv('GOOGLE_CLIENT_ID', '')))
"

# Check frontend environment
cd ~/workspace/TO-DO_LIST/frontend
echo "Frontend Google Client ID: $REACT_APP_GOOGLE_CLIENT_ID"
```

## 📱 **Production Deployment:**

For production deployment:

1. **Update authorized origins:**
   - Add your production domain (e.g., `https://yourdomain.com`)
   - Remove localhost URLs

2. **Use environment variables:**
   - Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` on your server
   - Use secure JWT secret key

3. **Enable HTTPS:**
   - Google OAuth requires HTTPS in production

## 🎉 **Expected Result:**

After following these steps, you should be able to:
- ✅ Click "Sign in with Google" 
- ✅ See Google's official login popup
- ✅ Login with shwetay1508@gmail.com or any Google account
- ✅ Access the Todo app with your Google profile
- ✅ See your Google profile picture in the app

## 📞 **Need Help?**

If you're still having issues:
1. Check the browser console for error messages
2. Check backend logs: `tail -f ~/workspace/TO-DO_LIST/backend/backend.log`
3. Verify your Google Cloud Console settings match the instructions above
4. Make sure both .env files contain the correct Client ID

The error you encountered is completely normal for development setup - it just means we need to configure real Google OAuth credentials! 🚀
