import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function ForgotPassword({ onBackToLogin }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/forgot-password`, {
        email: email.trim()
      });

      setMessage(response.data.message);
      setEmailSent(true);
      
      // Clear form
      setEmail('');
      
    } catch (error) {
      console.error('Forgot password error:', error);
      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else {
        setError('An error occurred. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>🔐 Forgot Password</h2>
          <p>Enter your email address and we'll send you a link to reset your password.</p>
        </div>

        {!emailSent ? (
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">📧 Email Address</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                required
                disabled={loading}
              />
            </div>

            {error && <div className="error-message">❌ {error}</div>}
            {message && <div className="success-message">✅ {message}</div>}

            <button 
              type="submit" 
              className="auth-button"
              disabled={loading}
            >
              {loading ? '📧 Sending...' : '📧 Send Reset Link'}
            </button>
          </form>
        ) : (
          <div className="success-container">
            <div className="success-icon">📧</div>
            <h3>Check Your Email!</h3>
            <p className="success-message">{message}</p>
            <div className="info-box">
              <h4>📋 What's Next?</h4>
              <ul>
                <li>🔍 Check your email inbox (and spam folder)</li>
                <li>📧 Click the reset link in the email</li>
                <li>🔐 Create a new password</li>
                <li>🚀 Login with your new password</li>
              </ul>
            </div>
            <div className="security-notice">
              <strong>🔒 Security Notice:</strong>
              <p>The reset link will expire in 1 hour for your security.</p>
            </div>
          </div>
        )}

        <div className="auth-links">
          <button 
            onClick={onBackToLogin}
            className="link-button"
            disabled={loading}
          >
            ← Back to Login
          </button>
        </div>

        {emailSent && (
          <div className="resend-section">
            <p>Didn't receive the email?</p>
            <button 
              onClick={() => {
                setEmailSent(false);
                setMessage('');
                setError('');
              }}
              className="link-button"
            >
              🔄 Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ForgotPassword;
