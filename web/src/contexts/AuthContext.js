import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
    const apiKey = localStorage.getItem('apiKey');
    if (apiKey) {
      api.defaults.headers.common['X-API-Key'] = apiKey;
      setCurrentUser({ apiKey });
    }
    setLoading(false);
  }, []);

  const login = async (apiKey) => {
    try {
      // Set API key in axios defaults
      api.defaults.headers.common['X-API-Key'] = apiKey;
      
      // Test the API key with a simple request
      await api.get('/system/health');
      
      // Save API key to local storage
      localStorage.setItem('apiKey', apiKey);
      
      // Set current user
      setCurrentUser({ apiKey });
      
      // Navigate to dashboard
      navigate('/');
      
      return true;
    } catch (err) {
      setError('Invalid API key');
      return false;
    }
  };

  const logout = () => {
    // Remove API key from axios defaults
    delete api.defaults.headers.common['X-API-Key'];
    
    // Remove API key from local storage
    localStorage.removeItem('apiKey');
    
    // Clear current user
    setCurrentUser(null);
    
    // Navigate to login page
    navigate('/login');
  };

  const value = {
    currentUser,
    login,
    logout,
    error,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
