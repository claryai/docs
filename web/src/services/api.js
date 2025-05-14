import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login
      localStorage.removeItem('apiKey');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Document API
export const documentApi = {
  // Upload a document
  uploadDocument: (file, templateId = null, options = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (templateId) {
      formData.append('template_id', templateId);
    }
    if (options) {
      formData.append('options', JSON.stringify(options));
    }
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get document status
  getDocumentStatus: (documentId) => {
    return api.get(`/documents/${documentId}`);
  },

  // Get document results
  getDocumentResults: (documentId) => {
    return api.get(`/documents/${documentId}/results`);
  },

  // Delete document
  deleteDocument: (documentId) => {
    return api.delete(`/documents/${documentId}`);
  },
};

// Template API
export const templateApi = {
  // Get all templates
  getTemplates: () => {
    return api.get('/templates');
  },

  // Get template by ID
  getTemplate: (templateId) => {
    return api.get(`/templates/${templateId}`);
  },

  // Create template
  createTemplate: (template) => {
    return api.post('/templates', template);
  },

  // Update template
  updateTemplate: (templateId, template) => {
    return api.put(`/templates/${templateId}`, template);
  },

  // Delete template
  deleteTemplate: (templateId) => {
    return api.delete(`/templates/${templateId}`);
  },
};

// System API
export const systemApi = {
  // Get system status
  getSystemStatus: () => {
    return api.get('/system/status');
  },

  // Get system health
  getSystemHealth: () => {
    return api.get('/health');
  },
};

export default api;
