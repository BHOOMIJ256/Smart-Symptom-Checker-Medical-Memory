import React, { useState, useRef, useEffect } from 'react';
import './SpeechToText.css';

const SpeechToText = ({ patientId, onSymptomsExtracted }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [extractedSymptoms, setExtractedSymptoms] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  // Cleanup function
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      setError('');
      setTranscription('');
      setExtractedSymptoms(null);
      setDiagnosis(null);
      setRecordingTime(0);
      audioChunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        // Use webm format which is more widely supported by MediaRecorder
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      setError('Failed to start recording. Please check microphone permissions.');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const processAudio = async () => {
    if (!audioBlob || !patientId) {
      setError('No audio recorded or patient ID missing');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('patient_id', patientId);

      const response = await fetch('http://localhost:8000/api/speech-to-symptoms', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setTranscription(result.transcription.transcribed_text);
        setExtractedSymptoms(result.extracted_symptoms);
        setDiagnosis(result.diagnosis);
        
        // Call parent callback if provided
        if (onSymptomsExtracted) {
          onSymptomsExtracted({
            transcription: result.transcription.transcribed_text,
            symptoms: result.extracted_symptoms,
            diagnosis: result.diagnosis
          });
        }
      } else {
        setError('Failed to process speech');
      }
    } catch (err) {
      setError(`Error processing audio: ${err.message}`);
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearRecording = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setTranscription('');
    setExtractedSymptoms(null);
    setDiagnosis(null);
    setRecordingTime(0);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
  };

  const renderSymptomCategory = (category, symptoms) => (
    <div key={category} className="symptom-category">
      <h4 className="category-title">{category.charAt(0).toUpperCase() + category.slice(1)}</h4>
      <ul className="symptom-list">
        {symptoms.map((symptom, index) => (
          <li key={index} className="symptom-item">{symptom}</li>
        ))}
      </ul>
    </div>
  );

  return (
    <div className="speech-to-text-container">
      <div className="speech-header">
        <h3>Voice Symptom Recorder</h3>
        <p>Record your symptoms by speaking into the microphone</p>
      </div>

      <div className="recording-section">
        <div className="recording-controls">
          {!isRecording && !audioBlob && (
            <button 
              className="record-button start"
              onClick={startRecording}
              disabled={isProcessing}
            >
              🎤 Start Recording
            </button>
          )}
          
          {isRecording && (
            <button 
              className="record-button stop"
              onClick={stopRecording}
            >
              ⏹️ Stop Recording ({formatTime(recordingTime)})
            </button>
          )}
          
          {audioBlob && !isRecording && (
            <div className="audio-controls">
              <button 
                className="process-button"
                onClick={processAudio}
                disabled={isProcessing}
              >
                {isProcessing ? '🔄 Processing...' : '🔍 Analyze Symptoms'}
              </button>
              <button 
                className="clear-button"
                onClick={clearRecording}
                disabled={isProcessing}
              >
                🗑️ Clear
              </button>
            </div>
          )}
        </div>

        {audioUrl && (
          <div className="audio-preview">
            <h4>Recording Preview:</h4>
            <audio controls src={audioUrl} className="audio-player" />
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {transcription && (
        <div className="transcription-section">
          <h4>Transcribed Text:</h4>
          <div className="transcription-text">
            "{transcription}"
          </div>
        </div>
      )}

      {extractedSymptoms && (
        <div className="symptoms-section">
          <h4>Extracted Symptoms:</h4>
          
          {extractedSymptoms.duration && (
            <div className="duration-info">
              <strong>Duration:</strong> {extractedSymptoms.duration}
            </div>
          )}
          
          {extractedSymptoms.severity_indicators && extractedSymptoms.severity_indicators.length > 0 && (
            <div className="severity-info">
              <strong>Severity:</strong> {extractedSymptoms.severity_indicators.join(', ')}
            </div>
          )}
          
          <div className="symptoms-summary">
            <strong>Total Symptoms Found:</strong> {extractedSymptoms.symptom_count}
          </div>
          
          <div className="symptoms-by-category">
            {Object.entries(extractedSymptoms.extracted_symptoms).map(([category, symptoms]) =>
              renderSymptomCategory(category, symptoms)
            )}
          </div>
        </div>
      )}

      {diagnosis && (
        <div className="diagnosis-section">
          <h4>AI Analysis:</h4>
          <div className="diagnosis-content">
            <div className="diagnosis-item">
              <strong>Possible Conditions:</strong>
              <ul>
                {diagnosis.possible_conditions?.map((condition, index) => (
                  <li key={index}>{condition}</li>
                ))}
              </ul>
            </div>
            
            {diagnosis.recommendations && (
              <div className="diagnosis-item">
                <strong>Recommendations:</strong>
                <ul>
                  {diagnosis.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {diagnosis.severity_level && (
              <div className="diagnosis-item">
                <strong>Severity Level:</strong> {diagnosis.severity_level}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SpeechToText; 