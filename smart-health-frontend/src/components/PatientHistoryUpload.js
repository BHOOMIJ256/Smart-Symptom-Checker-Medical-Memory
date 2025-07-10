import React, { useState } from 'react';
import './PatientHistoryUpload.css';

export default function PatientHistoryUpload({ user }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileType = selectedFile.type;
      const fileName = selectedFile.name.toLowerCase();
      
      // Check if file is PDF or image
      if (fileType === 'application/pdf' || 
          fileType.startsWith('image/') ||
          fileName.endsWith('.pdf') ||
          fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') ||
          fileName.endsWith('.png') || fileName.endsWith('.bmp') ||
          fileName.endsWith('.tiff')) {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please select a PDF or image file (JPG, PNG, BMP, TIFF)');
        setFile(null);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !user?.patient_id) return;

    setLoading(true);
    setResult(null);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('patient_id_form', user.patient_id);

    try {
      const response = await fetch(`http://localhost:8000/api/upload/${user.patient_id}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
    setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="upload-container">
      <div className="upload-card">
        <div className="upload-header">
          <h2>Upload Medical Records</h2>
          <p>Upload PDF documents or images (prescriptions, lab reports, etc.)</p>
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-upload-area">
            <input
              type="file"
              id="file-input"
              accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="file-input" className="file-label">
              <div className="upload-icon">📄</div>
              <div className="upload-text">
                <h3>Choose a file</h3>
                <p>PDF or Image (JPG, PNG, BMP, TIFF)</p>
                <span className="file-size-limit">Max 10MB</span>
              </div>
            </label>
          </div>

          {file && (
            <div className="selected-file">
              <div className="file-info">
                <span className="file-icon">
                  {file.type === 'application/pdf' ? '📄' : '📷'}
                </span>
                <div className="file-details">
                  <h4>{file.name}</h4>
                  <p>{formatFileSize(file.size)}</p>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="remove-file"
                >
                  ×
                </button>
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
            className="upload-button"
            disabled={loading || !file}
          >
            {loading ? 'Processing...' : 'Upload & Process'}
          </button>
      </form>

      {result && (
          <div className="result-section">
            <h3>Processing Results</h3>
            <div className="result-card">
              <div className="result-item">
                <span className="result-label">Status:</span>
                <span className="result-value success">✓ Successfully processed</span>
              </div>
              <div className="result-item">
                <span className="result-label">Document ID:</span>
                <span className="result-value">{result.document_id}</span>
              </div>
              <div className="result-item">
                <span className="result-label">File Type:</span>
                <span className="result-value">{result.file_type}</span>
              </div>
              <div className="result-item">
                <span className="result-label">File Size:</span>
                <span className="result-value">{formatFileSize(result.file_size)}</span>
              </div>
              
              {result.extracted_data && (
                <div className="extracted-data">
                  <h4>Extracted Medical Information:</h4>
                  <div className="data-grid">
                    {result.extracted_data.medical_conditions && (
                      <div className="data-item">
                        <strong>Medical Conditions:</strong>
                        <ul>
                          {result.extracted_data.medical_conditions.map((condition, index) => (
                            <li key={index}>{condition}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.extracted_data.medications && (
                      <div className="data-item">
                        <strong>Medications:</strong>
                        <ul>
                          {result.extracted_data.medications.map((med, index) => (
                            <li key={index}>{med}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.extracted_data.allergies && (
                      <div className="data-item">
                        <strong>Allergies:</strong>
                        <ul>
                          {result.extracted_data.allergies.map((allergy, index) => (
                            <li key={index}>{allergy}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.extracted_data.surgeries && (
                      <div className="data-item">
                        <strong>Surgeries:</strong>
                        <ul>
                          {result.extracted_data.surgeries.map((surgery, index) => (
                            <li key={index}>{surgery}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.extracted_data.lab_results && (
                      <div className="data-item">
                        <strong>Lab Results:</strong>
                        <ul>
                          {result.extracted_data.lab_results.map((lab, index) => (
                            <li key={index}>
                              {typeof lab === 'object' && lab.test && lab.value 
                                ? `${lab.test}: ${lab.value}${lab.unit ? ` ${lab.unit}` : ''}`
                                : typeof lab === 'string' 
                                  ? lab 
                                  : JSON.stringify(lab)
                              }
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {result.full_text && (
                <div className="full-text-section">
                  <h4>Full Extracted Text:</h4>
                  <div className="text-content">
                    {result.full_text}
                  </div>
                </div>
              )}
            </div>
          </div>
      )}
      </div>
    </div>
  );
} 