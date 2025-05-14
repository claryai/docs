import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Templates from './pages/Templates';
import Settings from './pages/Settings';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="documents" element={<Documents />} />
          <Route path="templates" element={<Templates />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
