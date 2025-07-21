import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Paper } from '@mui/material';
import axios from 'axios';

export default function SimilarCasesSearch() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(3);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResults(null);
    try {
      const { data } = await axios.post(`http://localhost:8000/search-cases?query=${encodeURIComponent(query)}&top_k=${topK}`);
      setResults(data);
    } catch (err) {
      setResults({ error: err.response?.data?.detail || 'Error contacting backend.' });
    }
    setLoading(false);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Search Similar Cases</Typography>
      <form onSubmit={handleSubmit}>
        <TextField label="Symptom Query" value={query} onChange={e => setQuery(e.target.value)} fullWidth required margin="normal" />
        <TextField label="Top K" value={topK} onChange={e => setTopK(e.target.value)} type="number" fullWidth margin="normal" />
        <Box sx={{ mt: 2 }}>
          <Button type="submit" variant="contained" disabled={loading}>Search</Button>
        </Box>
      </form>
      {results && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1">Results:</Typography>
          {Array.isArray(results) && results.length > 0 ? (
            results.map((caseItem, idx) => (
              <Paper key={caseItem.case_id || idx} sx={{ p: 2, mb: 2, background: '#f9f9f9' }} elevation={2}>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  Case ID: {caseItem.case_id}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Symptoms:</strong> {caseItem.symptoms || 'N/A'}
                </Typography>
                {caseItem.diagnosis && (
                  <Typography variant="body2"><strong>Diagnosis:</strong> {caseItem.diagnosis}</Typography>
                )}
                {caseItem.treatment && (
                  <Typography variant="body2"><strong>Treatment:</strong> {caseItem.treatment}</Typography>
                )}
                {caseItem.outcome && (
                  <Typography variant="body2"><strong>Outcome:</strong> {caseItem.outcome}</Typography>
                )}
                <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'gray' }}>
                  Created At: {caseItem.created_at ? new Date(caseItem.created_at).toLocaleString() : 'N/A'}
                </Typography>
              </Paper>
            ))
          ) : results.error ? (
            <Typography color="error">{results.error}</Typography>
          ) : (
            <Typography>No similar cases found.</Typography>
          )}
        </Box>
      )}
    </Paper>
  );
} 