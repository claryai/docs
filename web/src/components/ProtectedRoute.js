import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * ProtectedRoute component for protecting routes that require authentication.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @returns {React.ReactElement} The protected route component
 */
function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();
  
  if (!currentUser) {
    // Redirect to login page if not authenticated
    return <Navigate to="/login" />;
  }
  
  // Render children if authenticated
  return children;
}

export default ProtectedRoute;
