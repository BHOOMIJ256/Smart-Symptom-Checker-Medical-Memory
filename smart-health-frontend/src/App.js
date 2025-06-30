import React, { useState } from 'react';
import { Container, Tabs, Tab, Box, Typography } from '@mui/material';
import SymptomChecker from './components/SymptomChecker';
import PatientHistoryUpload from './components/PatientHistoryUpload';
import SimilarCasesSearch from './components/SimilarCasesSearch';

function App() {
  const [tab, setTab] = useState(0);

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        🩺 Smart Health AI
      </Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} centered>
        <Tab label="Symptom Checker" />
        <Tab label="Patient History Upload" />
        <Tab label="Similar Cases Search" />
      </Tabs>
      <Box sx={{ mt: 3 }}>
        {tab === 0 && <SymptomChecker />}
        {tab === 1 && <PatientHistoryUpload />}
        {tab === 2 && <SimilarCasesSearch />}
      </Box>
    </Container>
  );
}

export default App;