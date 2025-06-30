import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Paper } from '@mui/material';
import axios from 'axios';

export default function PatientHistoryUpload() {
  const [patientId, setPatientId] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('file', file);
    try {
      const { data } = await axios.post('http://localhost:8000/upload-patient-history', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Error contacting backend.' });
    }
    setLoading(false);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Upload Patient History (PDF)</Typography>
      <form onSubmit={handleSubmit}>
        <TextField label="Patient ID" value={patientId} onChange={e => setPatientId(e.target.value)} fullWidth required margin="normal" />
        <Button variant="contained" component="label" sx={{ mt: 2 }}>
          Select PDF
          <input type="file" accept="application/pdf" hidden onChange={e => setFile(e.target.files[0])} />
        </Button>
        <Box sx={{ mt: 2 }}>
          <Button type="submit" variant="contained" disabled={loading || !file}>Upload</Button>
        </Box>
      </form>
      {result && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1">Result:</Typography>
          <pre style={{ background: '#f5f5f5', padding: 10, borderRadius: 4 }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Box>
      )}
    </Paper>
  );
} 