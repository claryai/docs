import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { systemApi, documentApi } from '../services/api';

/**
 * Dashboard page component.
 * 
 * @returns {React.ReactElement} The dashboard page component
 */
function Dashboard() {
  const [systemStatus, setSystemStatus] = useState(null);
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // In a real implementation, fetch recent documents
        // For now, use mock data
        setRecentDocuments([
          {
            document_id: 'doc_123456',
            filename: 'invoice.pdf',
            status: 'completed',
            created_at: '2023-05-13T10:30:00Z',
          },
          {
            document_id: 'doc_789012',
            filename: 'receipt.pdf',
            status: 'processing',
            created_at: '2023-05-13T11:15:00Z',
          },
        ]);
        
        // Fetch system status
        const response = await systemApi.getSystemStatus();
        setSystemStatus(response.data);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <div className="text-red-700">{error}</div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Welcome to DocuAgent
        </h2>
        <p className="text-gray-600">
          DocuAgent is an open source document processing platform with agentic capabilities.
          Upload documents, extract structured data, and transform your workflow.
        </p>
        <div className="mt-4">
          <Link
            to="/documents"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Upload Document
          </Link>
        </div>
      </div>
      
      {/* System status */}
      {systemStatus && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            System Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm font-medium text-gray-500">Status</div>
              <div className="mt-1 text-lg font-semibold text-gray-900">
                {systemStatus.status}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm font-medium text-gray-500">Documents Processed</div>
              <div className="mt-1 text-lg font-semibold text-gray-900">
                {systemStatus.usage?.documents_processed_total || 0}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm font-medium text-gray-500">Storage Used</div>
              <div className="mt-1 text-lg font-semibold text-gray-900">
                {systemStatus.usage?.storage_used || '0MB'}
              </div>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-lg font-medium text-gray-800 mb-2">
              Components
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(systemStatus.components || {}).map(([key, value]) => (
                <div key={key} className="flex items-center">
                  <div className={`h-3 w-3 rounded-full mr-2 ${
                    value === 'running' || value === 'connected'
                      ? 'bg-green-500'
                      : 'bg-yellow-500'
                  }`}></div>
                  <div className="text-sm text-gray-600">
                    {key}: {value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Recent documents */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Recent Documents
        </h2>
        {recentDocuments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Filename
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentDocuments.map((doc) => (
                  <tr key={doc.document_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.filename}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        doc.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : doc.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <Link
                        to={`/documents/${doc.document_id}`}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-gray-500 text-center py-4">
            No documents found
          </div>
        )}
        <div className="mt-4">
          <Link
            to="/documents"
            className="text-indigo-600 hover:text-indigo-900"
          >
            View all documents
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
