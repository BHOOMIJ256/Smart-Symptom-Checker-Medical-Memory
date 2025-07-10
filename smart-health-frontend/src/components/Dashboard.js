import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { FaTrash } from 'react-icons/fa';

const Dashboard = ({ user, onLogout, onNavigateToSymptomChecker, onNavigateToUpload, onNavigateToImageAnalysis, onNavigateToSpeechToText }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingDocId, setDeletingDocId] = useState(null);

  useEffect(() => {
    if (user?.patient_id) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/dashboard/${user.patient_id}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDeleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    setDeletingDocId(documentId);
    try {
      const res = await fetch(
        `http://localhost:8000/api/documents/${user.patient_id}/${documentId}`,
        { method: 'DELETE' }
      );
      if (!res.ok) throw new Error('Failed to delete');
      setDashboardData((prev) => ({
        ...prev,
        recent_documents: prev.recent_documents.filter((doc) => doc.document_id !== documentId),
        total_documents: prev.total_documents - 1
      }));
    } catch (err) {
      alert('Failed to delete document.');
    } finally {
      setDeletingDocId(null);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading your health dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">
          <h3>Error loading dashboard</h3>
          <p>{error}</p>
          <button onClick={fetchDashboardData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="user-welcome">
          <h1>Welcome back, {user?.first_name || 'User'}! 👋</h1>
          <p>Your Patient ID: <strong>{user?.patient_id}</strong></p>
        </div>
        <div className="header-actions">
          <button onClick={onLogout} className="logout-button">
            Sign Out
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <div className="action-card" onClick={onNavigateToSymptomChecker}>
          <div className="action-icon">🩺</div>
          <h3>Check Symptoms</h3>
          <p>Get AI-powered health insights</p>
        </div>
        <div className="action-card" onClick={onNavigateToUpload}>
          <div className="action-icon">📄</div>
          <h3>Upload Records</h3>
          <p>Add medical documents & images</p>
        </div>
        <div className="action-card" onClick={onNavigateToImageAnalysis}>
          <div className="action-icon">📷</div>
          <h3>Image Analysis</h3>
          <p>Analyze skin conditions & rashes</p>
        </div>
        <div className="action-card" onClick={onNavigateToSpeechToText}>
          <div className="action-icon">🎤</div>
          <h3>Voice Recorder</h3>
          <p>Record symptoms with voice</p>
        </div>
      </div>

      {/* Health Summary */}
      <div className="dashboard-section">
        <h2>Health Summary</h2>
        <div className="health-summary">
          <div className="summary-card">
            <div className="summary-number">{dashboardData?.total_documents || 0}</div>
            <div className="summary-label">Documents Uploaded</div>
          </div>
          <div className="summary-card">
            <div className="summary-number">
              {dashboardData?.health_summary?.extraction_confidence_avg 
                ? `${Math.round(dashboardData.health_summary.extraction_confidence_avg * 100)}%`
                : '0%'
              }
            </div>
            <div className="summary-label">Data Quality</div>
          </div>
          <div className="summary-card">
            <div className="summary-number">
              {dashboardData?.recent_diagnoses?.length || 0}
            </div>
            <div className="summary-label">Recent Checks</div>
          </div>
        </div>
      </div>

      {/* Recent Documents */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent Documents</h2>
          <button onClick={onNavigateToUpload} className="upload-more-button">
            Upload More
          </button>
        </div>
        
        {dashboardData?.recent_documents?.length > 0 ? (
          <div className="documents-grid">
            {dashboardData.recent_documents.map((doc) => (
              <div key={doc.document_id} className="document-card">
                <div className="document-icon">
                  {doc.file_type === 'PDF' ? '📄' : '📷'}
                </div>
                <div className="document-info">
                  <h4>{doc.filename}</h4>
                  <p className="document-meta">
                    {doc.file_type} • {formatFileSize(doc.file_size)}
                  </p>
                  <p className="document-date">
                    Uploaded {formatDate(doc.upload_date)}
                  </p>
                  {doc.confidence_score > 0 && (
                    <div className="confidence-score">
                      Quality: {Math.round(doc.confidence_score * 100)}%
                    </div>
                  )}
                </div>
                <button
                  className="delete-doc-btn"
                  title="Delete Document"
                  onClick={() => handleDeleteDocument(doc.document_id)}
                  disabled={deletingDocId === doc.document_id}
                >
                  <FaTrash />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">📄</div>
            <h3>No documents yet</h3>
            <p>Upload your medical records to get started</p>
            <button onClick={onNavigateToUpload} className="primary-button">
              Upload First Document
            </button>
          </div>
        )}
      </div>

      {/* User Profile */}
      <div className="dashboard-section">
        <h2>Profile Information</h2>
        <div className="profile-card">
          <div className="profile-info">
            <div className="info-row">
              <span className="info-label">Name:</span>
              <span className="info-value">
                {user?.first_name} {user?.last_name}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Email:</span>
              <span className="info-value">{user?.email}</span>
            </div>
            {user?.phone && (
              <div className="info-row">
                <span className="info-label">Phone:</span>
                <span className="info-value">{user.phone}</span>
              </div>
            )}
            {user?.age && (
              <div className="info-row">
                <span className="info-label">Age:</span>
                <span className="info-value">{user.age} years</span>
              </div>
            )}
            {user?.gender && (
              <div className="info-row">
                <span className="info-label">Gender:</span>
                <span className="info-value">{user.gender}</span>
              </div>
            )}
            {user?.chronic_conditions?.length > 0 && (
              <div className="info-row">
                <span className="info-label">Conditions:</span>
                <span className="info-value">
                  {user.chronic_conditions.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 