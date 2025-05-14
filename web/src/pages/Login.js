import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

/**
 * Login page component.
 * 
 * @returns {React.ReactElement} The login page component
 */
function Login() {
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAuth();
  
  /**
   * Handle form submission.
   * 
   * @param {React.FormEvent} e - Form event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      return;
    }
    
    setIsLoading(true);
    
    try {
      await login(apiKey);
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            DocuAgent
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="api-key" className="sr-only">
                API Key
              </label>
              <input
                id="api-key"
                name="apiKey"
                type="password"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
          </div>
          
          {error && (
            <div className="text-red-500 text-sm text-center">{error}</div>
          )}
          
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className={`group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                isLoading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          
          <div className="text-sm text-center">
            <p className="text-gray-600">
              For development, use API key: <code>dev_api_key</code>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Login;
