import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Main layout component with navigation sidebar and content area.
 * 
 * @returns {React.ReactElement} The layout component
 */
function Layout() {
  const { logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Navigation items
  const navItems = [
    { path: '/', label: 'Dashboard', icon: 'home' },
    { path: '/documents', label: 'Documents', icon: 'document' },
    { path: '/templates', label: 'Templates', icon: 'template' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];
  
  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  // Handle logout
  const handleLogout = () => {
    logout();
  };
  
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64 bg-gray-800">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 bg-gray-900">
            <span className="text-white font-bold text-lg">DocuAgent</span>
          </div>
          
          {/* Navigation */}
          <div className="flex flex-col flex-grow">
            <nav className="flex-1 px-2 py-4 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                    location.pathname === item.path
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
            
            {/* Logout button */}
            <div className="p-4">
              <button
                onClick={handleLogout}
                className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-700 hover:text-white"
              >
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className="md:hidden">
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-40 flex">
            {/* Overlay */}
            <div
              className="fixed inset-0 bg-gray-600 bg-opacity-75"
              onClick={toggleMobileMenu}
            ></div>
            
            {/* Sidebar */}
            <div className="relative flex-1 flex flex-col max-w-xs w-full bg-gray-800">
              {/* Close button */}
              <div className="absolute top-0 right-0 -mr-12 pt-2">
                <button
                  className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                  onClick={toggleMobileMenu}
                >
                  <span className="sr-only">Close sidebar</span>
                  <span className="text-white">×</span>
                </button>
              </div>
              
              {/* Logo */}
              <div className="flex items-center justify-center h-16 bg-gray-900">
                <span className="text-white font-bold text-lg">DocuAgent</span>
              </div>
              
              {/* Navigation */}
              <div className="flex-1 h-0 overflow-y-auto">
                <nav className="px-2 py-4 space-y-1">
                  {navItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center px-4 py-2 text-sm font-medium rounded-md ${
                        location.pathname === item.path
                          ? 'bg-gray-900 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      }`}
                      onClick={toggleMobileMenu}
                    >
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </nav>
                
                {/* Logout button */}
                <div className="p-4">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-4 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-700 hover:text-white"
                  >
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Content area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top header */}
        <div className="flex items-center justify-between h-16 bg-white border-b border-gray-200 px-4 md:px-6">
          {/* Mobile menu button */}
          <button
            className="md:hidden text-gray-500 hover:text-gray-900 focus:outline-none"
            onClick={toggleMobileMenu}
          >
            <span className="sr-only">Open sidebar</span>
            <svg
              className="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
          
          {/* Page title */}
          <h1 className="text-lg font-semibold text-gray-900">
            {navItems.find((item) => item.path === location.pathname)?.label || 'Dashboard'}
          </h1>
          
          {/* User menu (placeholder) */}
          <div className="ml-4 flex items-center md:ml-6">
            <div className="bg-gray-200 rounded-full h-8 w-8 flex items-center justify-center">
              <span className="text-sm font-medium text-gray-600">U</span>
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-100">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
