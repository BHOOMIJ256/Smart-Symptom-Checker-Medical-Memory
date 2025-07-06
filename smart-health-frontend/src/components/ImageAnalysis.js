import React, { useState } from 'react';
import './ImageAnalysis.css';

export default function ImageAnalysis({ user }) {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [imageType, setImageType] = useState('skin');

  const imageTypes = [
    { value: 'skin', label: 'Skin Condition' },
    { value: 'rash', label: 'Rash' },
    { value: 'wound', label: 'Wound' },
    { value: 'dermatological', label: 'Dermatological' }
  ];

  const handleImageChange = (e) => {
    const selectedImage = e.target.files[0];
    if (selectedImage) {
      const fileType = selectedImage.type;
      const fileName = selectedImage.name.toLowerCase();
      
      // Check if file is an image
      if (fileType.startsWith('image/') ||
          fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') ||
          fileName.endsWith('.png') || fileName.endsWith('.bmp') ||
          fileName.endsWith('.tiff')) {
        setImage(selectedImage);
        setError('');
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreview(e.target.result);
        };
        reader.readAsDataURL(selectedImage);
      } else {
        setError('Please select an image file (JPG, PNG, BMP, TIFF)');
        setImage(null);
        setImagePreview(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image || !user?.patient_id) return;

    setLoading(true);
    setAnalysisResult(null);
    setError('');

    const formData = new FormData();
    formData.append('image', image);
    formData.append('image_type', imageType);
    if (user.patient_id) {
      formData.append('patient_id', user.patient_id);
    }

    try {
      const response = await fetch('http://localhost:8000/api/analyze-image', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysisResult(data.analysis);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
      case 'critical':
        return '#dc3545';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  return (
    <div className="image-analysis-container">
      <div className="image-analysis-card">
        <div className="analysis-header">
          <h2>AI Image Analysis</h2>
          <p>Upload medical images for AI-powered skin condition analysis</p>
        </div>

        <form onSubmit={handleSubmit} className="analysis-form">
          <div className="image-type-selector">
            <label htmlFor="image-type">Image Type:</label>
            <select
              id="image-type"
              value={imageType}
              onChange={(e) => setImageType(e.target.value)}
              className="image-type-select"
            >
              {imageTypes.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="image-upload-area">
            <input
              type="file"
              id="image-input"
              accept="image/*"
              onChange={handleImageChange}
              className="image-input"
            />
            <label htmlFor="image-input" className="image-label">
              <div className="upload-icon">📷</div>
              <div className="upload-text">
                <h3>Choose an image</h3>
                <p>Upload medical images for analysis</p>
                <span className="file-size-limit">Max 10MB</span>
              </div>
            </label>
          </div>

          {imagePreview && (
            <div className="image-preview">
              <h4>Image Preview:</h4>
              <div className="preview-container">
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  className="preview-image"
                />
                <div className="image-info">
                  <p><strong>File:</strong> {image.name}</p>
                  <p><strong>Type:</strong> {imageType}</p>
                  <p><strong>Size:</strong> {(image.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="analyze-button"
            disabled={loading || !image}
          >
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </form>

        {analysisResult && (
          <div className="analysis-result">
            <h3>Analysis Results</h3>
            <div className="result-card">
              <div className="result-header">
                <div className="severity-indicator">
                  <span 
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(analysisResult.severity_level) }}
                  >
                    {analysisResult.severity_level?.toUpperCase() || 'UNKNOWN'}
                  </span>
                  <span className="timestamp">
                    {new Date(analysisResult.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="detected-conditions">
                <h4>Detected Conditions:</h4>
                {analysisResult.detected_conditions && analysisResult.detected_conditions.length > 0 ? (
                  <div className="conditions-list">
                    {analysisResult.detected_conditions.map((condition, index) => (
                      <div key={index} className="condition-item">
                        <div className="condition-header">
                          <span className="condition-name">{condition.condition}</span>
                          <span className="confidence-score">
                            {formatConfidence(condition.confidence)}
                          </span>
                        </div>
                        {condition.area_percentage && (
                          <p className="area-info">
                            Affected area: {condition.area_percentage.toFixed(1)}%
                          </p>
                        )}
                        {condition.texture_variance && (
                          <p className="texture-info">
                            Texture variance: {condition.texture_variance.toFixed(0)}
                          </p>
                        )}
                        {condition.edge_density && (
                          <p className="edge-info">
                            Edge density: {(condition.edge_density * 100).toFixed(1)}%
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-conditions">No specific conditions detected</p>
                )}
              </div>

              {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                <div className="recommendations">
                  <h4>Recommendations:</h4>
                  <ul className="recommendations-list">
                    {analysisResult.recommendations.map((recommendation, index) => (
                      <li key={index} className="recommendation-item">
                        {recommendation}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="confidence-overview">
                <h4>Analysis Confidence:</h4>
                <div className="confidence-bars">
                  {analysisResult.confidence_scores && analysisResult.confidence_scores.map((score, index) => (
                    <div key={index} className="confidence-bar">
                      <span className="bar-label">Detection {index + 1}</span>
                      <div className="bar-container">
                        <div 
                          className="bar-fill"
                          style={{ width: `${score * 100}%` }}
                        ></div>
                      </div>
                      <span className="bar-value">{formatConfidence(score)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="medical-disclaimer">
                <p><strong>Medical Disclaimer:</strong></p>
                <p>
                  This AI analysis is for informational purposes only and should not replace 
                  professional medical diagnosis. Always consult with a qualified healthcare 
                  provider for proper diagnosis and treatment.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 