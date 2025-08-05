import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [tokenValid, setTokenValid] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [resetSuccess, setResetSuccess] = useState(false);
  
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get token from URL parameters
  const urlParams = new URLSearchParams(location.search);
  const token = urlParams.get('token');

  useEffect(() => {
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
      setVerifying(false);
      return;
    }

    // Verify token on component mount
    verifyToken();
  }, [token]);

  const verifyToken = async () => {
    try {
      setVerifying(true);
      const response = await axios.post(`${API_BASE_URL}/api/verify-reset-token`, {
        token: token
      });

      if (response.data.valid) {
        setTokenValid(true);
        setUserInfo({
          email: response.data.email,
          username: response.data.username
        });
      } else {
        setError(response.data.error || 'Invalid reset token');
      }
    } catch (error) {
      console.error('Token verification error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('Unable to verify reset token. Please try again.');
      }
    } finally {
      setVerifying(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!password.trim()) {
      setError('Please enter a new password');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/reset-password`, {
        token: token,
        password: password
      });

      setMessage(response.data.message);
      setResetSuccess(true);
      
      // Clear form
      setPassword('');
      setConfirmPassword('');
      
    } catch (error) {
      console.error('Password reset error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('An error occurred while resetting your password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate('/');
  };

  if (verifying) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h2>🔐 Verifying Reset Link</h2>
            <div className="loading-spinner">⏳ Please wait...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!tokenValid) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h2>❌ Invalid Reset Link</h2>
            <p>{error}</p>
          </div>
          <div className="error-container">
            <div className="error-icon">🔗</div>
            <h3>Reset Link Issues</h3>
            <div className="info-box">
              <h4>📋 Possible Reasons:</h4>
              <ul>
                <li>🕒 The reset link has expired (links expire after 1 hour)</li>
                <li>🔗 The link has already been used</li>
                <li>📧 The link was copied incorrectly</li>
                <li>🔄 A newer reset request was made</li>
              </ul>
            </div>
            <div className="auth-links">
              <button 
                onClick={handleBackToLogin}
                className="auth-button"
              >
                🏠 Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (resetSuccess) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h2>✅ Password Reset Successful</h2>
          </div>
          <div className="success-container">
            <div className="success-icon">🎉</div>
            <h3>Password Updated!</h3>
            <p className="success-message">{message}</p>
            <div className="info-box">
              <h4>📋 What's Next?</h4>
              <ul>
                <li>🚀 Click "Login Now" to access your account</li>
                <li>🔐 Use your new password to sign in</li>
                <li>📝 Start managing your todos!</li>
              </ul>
            </div>
            <div className="auth-links">
              <button 
                onClick={handleBackToLogin}
                className="auth-button"
              >
                🚀 Login Now
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>🔐 Reset Password</h2>
          {userInfo && (
            <div className="user-info">
              <p>👋 Hello <strong>{userInfo.username}</strong>!</p>
              <p>📧 Resetting password for: <strong>{userInfo.email}</strong></p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="password">🔒 New Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your new password"
              required
              disabled={loading}
              minLength="6"
            />
            <small className="form-hint">Password must be at least 6 characters long</small>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">🔒 Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your new password"
              required
              disabled={loading}
              minLength="6"
            />
          </div>

          {error && <div className="error-message">❌ {error}</div>}
          {message && <div className="success-message">✅ {message}</div>}

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? '🔄 Updating...' : '🔐 Update Password'}
          </button>
        </form>

        <div className="auth-links">
          <button 
            onClick={handleBackToLogin}
            className="link-button"
            disabled={loading}
          >
            ← Back to Login
          </button>
        </div>

        <div className="security-notice">
          <strong>🔒 Security Notice:</strong>
          <p>After updating your password, you'll need to login again on all devices.</p>
        </div>
      </div>
    </div>
  );
}

export default ResetPassword;
