import React, { useState } from 'react';
import { TextField, Button, MenuItem, Box, Typography, Paper } from '@mui/material';
import axios from 'axios';

const severityLevels = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

export default function SymptomChecker() {
  const [form, setForm] = useState({
    symptoms: '',
    patient_id: '',
    severity_level: 'medium',
    additional_context: '',
    age: '',
    gender: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const { data } = await axios.post('http://localhost:8000/analyze-symptoms', {
        ...form,
        age: form.age ? Number(form.age) : undefined,
      });
      setResult(data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Error contacting backend.' });
    }
    setLoading(false);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Symptom Checker</Typography>
      <form onSubmit={handleSubmit}>
        <TextField label="Symptoms" name="symptoms" value={form.symptoms} onChange={handleChange} fullWidth required margin="normal" />
        <TextField label="Patient ID" name="patient_id" value={form.patient_id} onChange={handleChange} fullWidth margin="normal" />
        <TextField select label="Severity Level" name="severity_level" value={form.severity_level} onChange={handleChange} fullWidth margin="normal">
          {severityLevels.map(opt => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
        </TextField>
        <TextField label="Additional Context" name="additional_context" value={form.additional_context} onChange={handleChange} fullWidth margin="normal" />
        <TextField label="Age" name="age" value={form.age} onChange={handleChange} type="number" fullWidth margin="normal" />
        <TextField label="Gender" name="gender" value={form.gender} onChange={handleChange} fullWidth margin="normal" />
        <Box sx={{ mt: 2 }}>
          <Button type="submit" variant="contained" disabled={loading}>Analyze</Button>
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