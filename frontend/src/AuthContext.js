import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => {
    // Clean up any potentially corrupted tokens on app start
    const storedToken = localStorage.getItem('token');
    if (storedToken && storedToken.length < 50) {
      // Token seems too short, probably corrupted
      localStorage.removeItem('token');
      return null;
    }
    // Set axios header immediately if token exists
    if (storedToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
    return storedToken;
  });
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Set up axios interceptor for authentication
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }

    // Add request interceptor to ensure token is always included
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const currentToken = localStorage.getItem('token');
        if (currentToken && !config.headers.Authorization) {
          config.headers.Authorization = `Bearer ${currentToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle token expiration
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401 || error.response?.status === 422) {
          const errorMsg = error.response?.data?.msg;
          if (errorMsg && (errorMsg.includes('expired') || errorMsg.includes('revoked') || errorMsg.includes('Invalid'))) {
            logout();
          }
        }
        return Promise.reject(error);
      }
    );

    // Cleanup interceptors
    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [token]);

  // Check if user is logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API_BASE_URL}/api/me`);
          setUser(response.data.user);
        } catch (error) {
          console.error('Auth check failed:', error);
          // Only logout on specific authentication errors
          if (error.response?.status === 401 || error.response?.status === 422) {
            console.log('Token expired or invalid, logging out');
            logout();
          } else {
            console.log('Network or server error, keeping user logged in');
            // For network errors, keep the user logged in but show they're offline
          }
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token, API_BASE_URL]);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/login`, {
        username,
        password
      });

      const { access_token, user } = response.data;
      
      // Set token immediately and synchronously
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setToken(access_token);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/register`, {
        username,
        email,
        password
      });

      const { access_token, user } = response.data;
      
      // Set token immediately and synchronously
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setToken(access_token);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      console.error('Registration failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      };
    }
  };

  const googleAuth = async (googleData) => {
    try {
      // The Google auth is already handled in the GoogleAuth component
      // We just need to set the user data here
      const { access_token, user } = googleData;
      
      // Set token immediately and synchronously
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setToken(access_token);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      console.error('Google authentication failed:', error);
      return { 
        success: false, 
        error: error.message || 'Google authentication failed' 
      };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API_BASE_URL}/api/logout`);
      }
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const value = {
    user,
    token,
    login,
    register,
    googleAuth,
    logout,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
