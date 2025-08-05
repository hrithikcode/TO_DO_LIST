import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import GoogleAuth from './GoogleAuth';
import './Auth.css';

const Login = ({ onToggleMode, onForgotPassword }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, googleAuth } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.username, formData.password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleGoogleSuccess = async (googleData) => {
    setError('');
    setLoading(true);
    
    const result = await googleAuth(googleData);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleGoogleError = (error) => {
    setError(error);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Welcome Back!</h2>
        <p className="auth-subtitle">Sign in to your account</p>
        
        {error && <div className="error-message">{error}</div>}
        
        {/* Google OAuth Button */}
        <div className="google-auth-section">
          <GoogleAuth 
            onSuccess={handleGoogleSuccess}
            onError={handleGoogleError}
            buttonText="Sign in with Google"
          />
          
          <div className="divider">
            <span>or</span>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={loading}
            />
          </div>
          
          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        {/* Forgot Password Link */}
        <div className="forgot-password-section">
          <button 
            onClick={onForgotPassword}
            className="forgot-password-link"
            disabled={loading}
          >
            🔐 Forgot your password?
          </button>
        </div>
        
        <p className="auth-toggle">
          Don't have an account?{' '}
          <button 
            onClick={onToggleMode}
            className="toggle-link"
            disabled={loading}
          >
            Sign up here
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
