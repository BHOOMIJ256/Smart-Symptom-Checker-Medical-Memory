from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional, List
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv():
        pass

# Import our modules
from models.symptom_models import SymptomRequest, DiagnosisResponse, PatientHistory, SeverityLevel, MedicalCase
from services.symptom_checker import SymptomCheckerService
from services.memory_service import MedicalMemoryService
from services.image_service import ImageAnalysisService
from services.speech_service import SpeechToTextService
from services.pdf_service import PDFProcessingService

app = FastAPI(
    title="Smart Health AI - Symptom Checker",
    description="AI-powered symptom checker with medical memory and multimodal input support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
symptom_checker = SymptomCheckerService()
memory_service = MedicalMemoryService()
image_service = ImageAnalysisService()
speech_service = SpeechToTextService()
pdf_service = PDFProcessingService()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Smart Health AI - Symptom Checker API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/analyze-symptoms", response_model=DiagnosisResponse)
async def analyze_symptoms(request: SymptomRequest):
    """
    Analyze symptoms and provide diagnosis suggestions
    """
    try:
        # Get patient history if available
        patient_history = None
        if request.patient_id:
            patient_history = await memory_service.get_patient_history(request.patient_id)
        
        # Retrieve similar cases from FAISS
        similar_cases = await memory_service.search_similar_cases(request.symptoms, top_k=3)
        
        # Analyze symptoms, passing similar cases as context
        diagnosis = await symptom_checker.analyze_symptoms(
            symptoms=request.symptoms,
            patient_history=patient_history,
            severity_level=request.severity_level,
            similar_cases=similar_cases
        )
        
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")

@app.post("/upload-patient-history")
async def upload_patient_history(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and process patient medical history (PDF)
    """
    try:
        if file.filename and not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Process PDF and extract medical information
        medical_data = await pdf_service.process_medical_pdf(file)
        
        # Store in vector database
        await memory_service.store_patient_history(patient_id, medical_data)
        
        return {
            "message": "Patient history uploaded successfully",
            "patient_id": patient_id,
            "extracted_data": medical_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing patient history: {str(e)}")

@app.post("/analyze-image")
async def analyze_medical_image(
    patient_id: Optional[str] = Form(None),
    image: UploadFile = File(...),
    image_type: str = Form("skin")  # skin, rash, wound, etc.
):
    """
    Analyze medical images (skin conditions, rashes, etc.)
    """
    try:
        if image.content_type and not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Analyze image
        analysis_result = await image_service.analyze_medical_image(
            image_file=image,
            image_type=image_type
        )
        
        # Store in memory if patient_id provided
        if patient_id:
            await memory_service.store_image_analysis(patient_id, analysis_result)
        
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

@app.post("/speech-to-symptoms")
async def convert_speech_to_symptoms(
    patient_id: Optional[str] = Form(None),
    audio: UploadFile = File(...)
):
    """
    Convert speech input to symptoms text
    """
    try:
        if audio.content_type and not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Only audio files are supported")
        
        # Convert speech to text
        symptoms_text = await speech_service.speech_to_text(audio)
        
        # Analyze the extracted symptoms
        diagnosis = await symptom_checker.analyze_symptoms(
            symptoms=symptoms_text,
            patient_history=None,
            severity_level=SeverityLevel.MEDIUM
        )
        
        return {
            "extracted_symptoms": symptoms_text,
            "diagnosis": diagnosis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing speech: {str(e)}")

@app.get("/patient-history/{patient_id}")
async def get_patient_history(patient_id: str):
    """
    Retrieve patient medical history
    """
    try:
        history = await memory_service.get_patient_history(patient_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient history: {str(e)}")

@app.get("/symptom-categories")
async def get_symptom_categories():
    """
    Get available symptom categories for classification
    """
    categories = [
        "Respiratory",
        "Cardiovascular", 
        "Gastrointestinal",
        "Neurological",
        "Dermatological",
        "Musculoskeletal",
        "Endocrine",
        "Mental Health",
        "General"
    ]
    return {"categories": categories}

@app.post("/search-cases", response_model=List[MedicalCase])
async def search_similar_cases(query: str, top_k: int = 3):
    """
    Search for similar medical cases using FAISS vector search.
    """
    try:
        results = await memory_service.search_similar_cases(query, top_k=top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching similar cases: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
