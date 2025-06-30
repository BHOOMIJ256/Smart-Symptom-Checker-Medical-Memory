from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SymptomRequest(BaseModel):
    """Request model for symptom analysis"""
    symptoms: str = Field(..., description="Description of symptoms")
    patient_id: Optional[str] = Field(None, description="Patient identifier for history lookup")
    severity_level: SeverityLevel = Field(SeverityLevel.MEDIUM, description="Perceived severity level")
    additional_context: Optional[str] = Field(None, description="Additional medical context")
    age: Optional[int] = Field(None, description="Patient age")
    gender: Optional[str] = Field(None, description="Patient gender")

class DiagnosisResponse(BaseModel):
    """Response model for diagnosis analysis"""
    probable_diagnoses: List[Dict[str, Any]] = Field(..., description="List of probable diagnoses with confidence scores")
    severity_assessment: str = Field(..., description="AI-assessed severity level")
    recommended_actions: List[str] = Field(..., description="Recommended actions for the patient")
    suggested_tests: List[str] = Field(..., description="Suggested medical tests")
    urgency_level: str = Field(..., description="How urgent medical attention is needed")
    confidence_score: float = Field(..., description="Overall confidence in the analysis")
    disclaimer: str = Field(..., description="Medical disclaimer")
    timestamp: datetime = Field(default_factory=datetime.now)

class PatientHistory(BaseModel):
    """Model for patient medical history"""
    patient_id: str = Field(..., description="Patient identifier")
    medical_conditions: List[str] = Field(default=[], description="List of medical conditions")
    medications: List[str] = Field(default=[], description="Current medications")
    allergies: List[str] = Field(default=[], description="Known allergies")
    surgeries: List[str] = Field(default=[], description="Past surgeries")
    family_history: Dict[str, List[str]] = Field(default={}, description="Family medical history")
    lab_results: List[Dict[str, Any]] = Field(default=[], description="Laboratory test results")
    notes: str = Field(default="", description="Additional medical notes")
    last_updated: datetime = Field(default_factory=datetime.now)

class ImageAnalysisResult(BaseModel):
    """Model for medical image analysis results"""
    image_type: str = Field(..., description="Type of medical image")
    detected_conditions: List[Dict[str, Any]] = Field(..., description="Detected medical conditions")
    confidence_scores: List[float] = Field(..., description="Confidence scores for detections")
    recommendations: List[str] = Field(..., description="Medical recommendations based on image")
    severity_level: str = Field(..., description="Assessed severity from image")
    timestamp: datetime = Field(default_factory=datetime.now)

class SpeechAnalysisResult(BaseModel):
    """Model for speech-to-symptoms analysis"""
    extracted_text: str = Field(..., description="Extracted text from speech")
    symptoms_identified: List[str] = Field(..., description="Symptoms identified from speech")
    confidence: float = Field(..., description="Confidence in speech recognition")
    diagnosis: Optional[DiagnosisResponse] = Field(None, description="Diagnosis based on extracted symptoms")

class MedicalCase(BaseModel):
    """Model for storing medical cases in vector database"""
    case_id: str = Field(..., description="Unique case identifier")
    symptoms: str = Field(..., description="Patient symptoms")
    diagnosis: str = Field(..., description="Final diagnosis")
    treatment: str = Field(..., description="Treatment provided")
    outcome: str = Field(..., description="Treatment outcome")
    category: str = Field(..., description="Medical category")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding for similarity search")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now) 