import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Any, Dict, Optional, List
from models.symptom_models import PatientHistory, ImageAnalysisResult, MedicalCase
import logging

class MedicalMemoryService:
    """Service for storing and retrieving patient medical memory (history, images, etc.) with FAISS vector search."""

    def __init__(self):
        # In-memory storage for patient histories and image analyses
        self._patient_histories: Dict[str, PatientHistory] = {}
        self._image_analyses: Dict[str, list] = {}
        self._medical_cases: Dict[str, MedicalCase] = {}

        # FAISS index and embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.faiss_dim = 384  # Dimension for 'all-MiniLM-L6-v2'
        self.faiss_index = faiss.IndexFlatL2(self.faiss_dim)
        self.case_id_to_index: Dict[int, str] = {}  # Map FAISS index to case_id
        self._faiss_next_idx = 0
        self.logger = logging.getLogger("services.memory_service")

    async def store_patient_history(self, patient_id: str, medical_data: Any) -> None:
        """Store patient history (PDF-extracted or structured data) and add to FAISS."""
        # Convert to PatientHistory if needed
        if not isinstance(medical_data, PatientHistory):
            # Minimal conversion; expand as needed
            medical_data = PatientHistory(patient_id=patient_id, **medical_data)
        self._patient_histories[patient_id] = medical_data
        self.logger.info(f"[store_patient_history] Parsed PatientHistory for {patient_id}: {medical_data}")
        # Store as a medical case for vector search
        await self.store_medical_case_from_history(medical_data)

    async def get_patient_history(self, patient_id: str) -> Optional[PatientHistory]:
        """Retrieve patient history by ID"""
        return self._patient_histories.get(patient_id)

    async def store_image_analysis(self, patient_id: str, analysis_result: ImageAnalysisResult) -> None:
        """Store image analysis result for a patient"""
        self._image_analyses.setdefault(patient_id, []).append(analysis_result)

    async def get_image_analyses(self, patient_id: str) -> list:
        """Retrieve all image analyses for a patient"""
        return self._image_analyses.get(patient_id, [])

    async def store_medical_case_from_history(self, history: PatientHistory) -> None:
        """Store a medical case from patient history and add to FAISS."""
        case_id = f"case_{history.patient_id}"
        case_text = self._history_to_text(history)
        embedding = self._embed_text(case_text)
        # Add to FAISS
        self.faiss_index.add(np.array([embedding]).astype('float32'))
        self.case_id_to_index[self._faiss_next_idx] = case_id
        self._faiss_next_idx += 1
        # Store case
        self._medical_cases[case_id] = MedicalCase(
            case_id=case_id,
            symptoms=case_text,
            diagnosis="",
            treatment="",
            outcome="",
            category="patient_history",
            embedding=embedding.tolist(),
            metadata={"patient_id": history.patient_id}
        )
        self.logger.info(f"[store_medical_case_from_history] FAISS index size: {self.faiss_index.ntotal}")

    def _history_to_text(self, history: PatientHistory) -> str:
        """Convert patient history to a text string for embedding."""
        parts = [
            f"Conditions: {', '.join(history.medical_conditions)}",
            f"Medications: {', '.join(history.medications)}",
            f"Allergies: {', '.join(history.allergies)}",
            f"Surgeries: {', '.join(history.surgeries)}",
            f"Notes: {history.notes}"
        ]
        return " | ".join(parts)

    def _embed_text(self, text: str) -> np.ndarray:
        """Generate an embedding for the given text."""
        return self.embedding_model.encode([text])[0]

    async def search_similar_cases(self, query: str, top_k: int = 3) -> List[MedicalCase]:
        """Search for similar medical cases using FAISS."""
        self.logger.info(f"[search_similar_cases] Query: {query}")
        if self.faiss_index.ntotal == 0:
            self.logger.info("[search_similar_cases] FAISS index is empty.")
            return []
        query_vec = self._embed_text(query)
        D, I = self.faiss_index.search(np.array([query_vec]).astype('float32'), top_k)
        results = []
        for idx in I[0]:
            if idx in self.case_id_to_index:
                case_id = self.case_id_to_index[idx]
                case = self._medical_cases.get(case_id)
                if case:
                    results.append(case)
        self.logger.info(f"[search_similar_cases] Results found: {len(results)}")
        return results 