# Google OAuth Setup Guide

## Overview
This Todo app now supports Google Single Sign-On (SSO) authentication alongside traditional email/password login.

## Features Added
- ✅ **Google OAuth Integration**: Login/Register with Google accounts
- ✅ **Dual Authentication**: Support both Google and traditional login
- ✅ **User Profile Pictures**: Automatically fetch Google profile pictures
- ✅ **Seamless Experience**: Same JWT token system for both auth methods
- ✅ **Account Linking Prevention**: Prevents conflicts between Google and local accounts

## How to Set Up Google OAuth (For Production)

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure OAuth consent screen
6. Add authorized origins:
   - `http://localhost:3000` (for development)
   - `https://yourdomain.com` (for production)

### 2. Configure Environment Variables

Create a `.env` file in the backend directory:
```bash
# Backend (.env)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-super-secret-jwt-key
```

Create a `.env` file in the frontend directory:
```bash
# Frontend (.env)
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
```

### 3. Update Configuration

The app is already configured to use environment variables. For development, it uses placeholder values.

## Current Development Setup

For development and testing, the app uses placeholder Google Client ID. The Google OAuth button will appear but won't work with real Google authentication until you configure actual credentials.

### Test the Implementation

1. **Regular Authentication**: Still works as before
   - Username: `testuser`
   - Password: `password123`

2. **Google OAuth UI**: The Google button appears on login/register pages
   - Shows proper UI integration
   - Handles errors gracefully
   - Ready for real Google credentials

## Database Schema Updates

The User model now includes:
- `google_id`: Stores Google user ID
- `profile_picture`: Stores Google profile picture URL
- `auth_provider`: Tracks authentication method ('local' or 'google')
- `password_hash`: Now nullable for Google users

## API Endpoints

### New Google OAuth Endpoint
```
POST /api/auth/google
Content-Type: application/json

{
  "token": "google_oauth_token"
}

Response:
{
  "access_token": "jwt_token",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@gmail.com",
    "profile_picture": "https://lh3.googleusercontent.com/...",
    "auth_provider": "google"
  },
  "message": "Login successful"
}
```

## Security Features

- ✅ **Token Verification**: Validates Google tokens server-side
- ✅ **Account Isolation**: Google and local accounts are separate
- ✅ **Email Conflict Prevention**: Prevents duplicate emails across auth methods
- ✅ **JWT Integration**: Same token system for all authentication methods
- ✅ **7-day Sessions**: Extended session duration for better UX

## Frontend Components

### New Components Added
- `GoogleAuth.js`: Google OAuth button component
- Updated `Login.js`: Includes Google OAuth option
- Updated `Register.js`: Includes Google OAuth option
- Enhanced `AuthContext.js`: Supports Google authentication

### UI Features
- Google OAuth buttons with proper styling
- "or" divider between Google and traditional auth
- Error handling for Google authentication
- Loading states for Google auth process

## Testing

### Current Status
- ✅ Backend Google OAuth endpoint working
- ✅ Frontend Google OAuth UI integrated
- ✅ Regular authentication still working
- ✅ Database schema updated
- ✅ Error handling implemented

### To Test with Real Google OAuth
1. Set up Google OAuth credentials (see setup steps above)
2. Update environment variables
3. Restart both backend and frontend
4. Test Google login/register functionality

## Production Deployment

When deploying to production:
1. Set up proper Google OAuth credentials
2. Configure environment variables on your server
3. Update authorized origins in Google Console
4. Use HTTPS for production URLs
5. Set secure JWT secret key

## Troubleshooting

### Common Issues
1. **"Invalid Google token"**: Check Google Client ID configuration
2. **CORS errors**: Ensure authorized origins are set correctly
3. **Token verification fails**: Verify Google Client ID matches frontend/backend
4. **Account conflicts**: App prevents email conflicts automatically

### Development Mode
- Uses placeholder Google Client ID
- Google OAuth button appears but won't authenticate
- Regular authentication works normally
- Ready for real Google credentials when configured
