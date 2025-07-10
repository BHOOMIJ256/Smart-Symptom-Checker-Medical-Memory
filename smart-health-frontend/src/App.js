import React, { useState, useEffect } from 'react';
import './App.css';
import UserAuth from './components/UserAuth';
import Dashboard from './components/Dashboard';
import SymptomChecker from './components/SymptomChecker';
import PatientHistoryUpload from './components/PatientHistoryUpload';
import SimilarCasesSearch from './components/SimilarCasesSearch';
import ImageAnalysis from './components/ImageAnalysis';
import SpeechToText from './components/SpeechToText';

function App() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('auth'); // auth, dashboard, symptom-checker, upload, search, image-analysis, speech-to-text
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setCurrentView('dashboard');
      } catch (error) {
        console.error('Error parsing saved user data:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setCurrentView('auth');
  };

  const handleNavigateToSymptomChecker = () => {
    setCurrentView('symptom-checker');
  };

  const handleNavigateToUpload = () => {
    setCurrentView('upload');
  };

  const handleNavigateToSearch = () => {
    setCurrentView('search');
  };

  const handleNavigateToImageAnalysis = () => {
    setCurrentView('image-analysis');
  };

  const handleNavigateToSpeechToText = () => {
    setCurrentView('speech-to-text');
  };

  const handleNavigateToDashboard = () => {
    setCurrentView('dashboard');
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading Smart Health AI...</p>
        </div>
      </div>
    );
  }

  // Render authentication if no user
  if (!user) {
    return <UserAuth onAuthSuccess={handleAuthSuccess} />;
  }

  // Render main app with navigation
  return (
    <div className="app">
      {/* Navigation Header */}
      <nav className="app-nav">
        <div className="nav-brand">
          <h1>🩺 Smart Health AI</h1>
        </div>
        <div className="nav-menu nav-menu-right">
          <button 
            className={`nav-button ${currentView === 'dashboard' ? 'active' : ''}`}
            onClick={handleNavigateToDashboard}
          >
            Dashboard
          </button>
          <button 
            className={`nav-button ${currentView === 'symptom-checker' ? 'active' : ''}`}
            onClick={handleNavigateToSymptomChecker}
          >
            Symptom Checker
          </button>
          <button 
            className={`nav-button ${currentView === 'upload' ? 'active' : ''}`}
            onClick={handleNavigateToUpload}
          >
            Upload Records
          </button>
          <button 
            className={`nav-button ${currentView === 'search' ? 'active' : ''}`}
            onClick={handleNavigateToSearch}
          >
            Search Cases
          </button>
          <button 
            className={`nav-button ${currentView === 'image-analysis' ? 'active' : ''}`}
            onClick={handleNavigateToImageAnalysis}
          >
            Image Analysis
          </button>
          <button 
            className={`nav-button ${currentView === 'speech-to-text' ? 'active' : ''}`}
            onClick={handleNavigateToSpeechToText}
          >
            Voice Recorder
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="app-main">
        {currentView === 'dashboard' && (
          <Dashboard 
            user={user}
            onLogout={handleLogout}
            onNavigateToSymptomChecker={handleNavigateToSymptomChecker}
            onNavigateToUpload={handleNavigateToUpload}
            onNavigateToImageAnalysis={handleNavigateToImageAnalysis}
            onNavigateToSpeechToText={handleNavigateToSpeechToText}
          />
        )}
        {currentView === 'symptom-checker' && (
          <div className="view-container">
            <div className="view-header">
              <button onClick={handleNavigateToDashboard} className="back-button">
                ← Back to Dashboard
              </button>
              <h2>Symptom Checker</h2>
            </div>
            <SymptomChecker user={user} />
          </div>
        )}
        {currentView === 'upload' && (
          <div className="view-container">
            <div className="view-header">
              <button onClick={handleNavigateToDashboard} className="back-button">
                ← Back to Dashboard
              </button>
              <h2>Upload Medical Records</h2>
            </div>
            <PatientHistoryUpload user={user} />
          </div>
        )}
        {currentView === 'search' && (
          <div className="view-container">
            <div className="view-header">
              <button onClick={handleNavigateToDashboard} className="back-button">
                ← Back to Dashboard
              </button>
              <h2>Search Similar Cases</h2>
            </div>
            <SimilarCasesSearch />
          </div>
        )}
        {currentView === 'image-analysis' && (
          <div className="view-container">
            <div className="view-header">
              <button onClick={handleNavigateToDashboard} className="back-button">
                ← Back to Dashboard
              </button>
              <h2>Image Analysis</h2>
            </div>
            <ImageAnalysis user={user} />
          </div>
        )}
        {currentView === 'speech-to-text' && (
          <div className="view-container">
            <div className="view-header">
              <button onClick={handleNavigateToDashboard} className="back-button">
                ← Back to Dashboard
              </button>
              <h2>Voice Symptom Recorder</h2>
            </div>
            <SpeechToText patientId={user.patient_id} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;