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
          <pre style={{ background: '#f5f5f5', padding: 10, borderRadius: 4 }}>
            {JSON.stringify(results, null, 2)}
          </pre>
        </Box>
      )}
    </Paper>
  );
} 