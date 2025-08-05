import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const GoogleAuth = ({ onSuccess, onError, buttonText = "Continue with Google" }) => {
  
  // Check if Google OAuth is properly configured
  const isGoogleConfigured = GOOGLE_CLIENT_ID && 
    GOOGLE_CLIENT_ID !== 'your-google-client-id.apps.googleusercontent.com' &&
    GOOGLE_CLIENT_ID.includes('.apps.googleusercontent.com');

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      console.log('Google login success:', credentialResponse);
      
      // Send the credential to our backend
      const response = await axios.post(`${API_BASE_URL}/api/auth/google`, {
        token: credentialResponse.credential
      });

      if (response.data.access_token) {
        onSuccess(response.data);
      } else {
        onError('Failed to authenticate with Google');
      }
    } catch (error) {
      console.error('Google authentication error:', error);
      const errorMessage = error.response?.data?.error || 'Google authentication failed';
      onError(errorMessage);
    }
  };

  const handleGoogleError = () => {
    console.error('Google login failed');
    onError('Google login was cancelled or failed');
  };

  const handleConfigurationClick = () => {
    onError('Google OAuth is not configured. Please follow the setup instructions in GOOGLE_OAUTH_SETUP.md');
  };

  // If Google OAuth is not configured, show a placeholder button
  if (!isGoogleConfigured) {
    return (
      <div className="google-auth-container">
        <button 
          type="button"
          className="google-oauth-placeholder"
          onClick={handleConfigurationClick}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '2px solid #ddd',
            borderRadius: '8px',
            backgroundColor: '#f8f9fa',
            color: '#666',
            fontSize: '16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
        >
          <span style={{ fontSize: '18px' }}>🔧</span>
          Configure Google OAuth
        </button>
        <p style={{ 
          fontSize: '12px', 
          color: '#999', 
          textAlign: 'center', 
          marginTop: '8px',
          marginBottom: '0'
        }}>
          Click to see setup instructions
        </p>
      </div>
    );
  }

  return (
    <div className="google-auth-container">
      <GoogleLogin
        onSuccess={handleGoogleSuccess}
        onError={handleGoogleError}
        useOneTap={false}
        theme="outline"
        size="large"
        text={buttonText === "Continue with Google" ? "continue_with" : "signin_with"}
        shape="rectangular"
        logo_alignment="left"
      />
    </div>
  );
};

export default GoogleAuth;
