from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional, List
import os
import logging

print("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    def load_dotenv() -> bool:
        return True

# Import our modules
from models.symptom_models import SymptomRequest, DiagnosisResponse, PatientHistory, SeverityLevel, MedicalCase
from models.user_models import UserRegistration, UserLogin, UserProfile, UserDashboard
from services.symptom_checker import SymptomCheckerService
from services.memory_service import MedicalMemoryService
from services.image_service import ImageAnalysisService
from services.speech_service import SpeechToTextService
from services.pdf_service import PDFProcessingService
from services.ocr_service import OCRService
from services.user_service import UserService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Health AI - Symptom Checker",
    description="AI-powered symptom checker with medical memory and multimodal input support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
ocr_service = OCRService()
user_service = UserService()

# Dependency to get current user (placeholder for now)
async def get_current_user(patient_id: str = Form(...)):
    """Get current user by patient ID."""
    user = await user_service.get_user_profile(patient_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid patient ID")
    return user

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
        # Save diagnosis to user history if patient_id present
        if request.patient_id:
            try:
                await user_service.save_user_diagnosis(request.patient_id, request.symptoms, diagnosis.dict())
            except Exception as e:
                logger.warning(f"Failed to save diagnosis for user: {e}")
        return diagnosis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")

@app.post("/upload-patient-history")
async def upload_patient_history(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload and process patient medical history (PDF or Image)
    """
    try:
        # Check file type
        if file.content_type:
            if file.content_type.startswith('image/'):
                # Handle image upload with OCR
                return await process_image_upload(patient_id, file)
            elif file.content_type == 'application/pdf':
                # Handle PDF upload
                return await process_pdf_upload(patient_id, file)
            else:
                raise HTTPException(status_code=400, detail="Only PDF and image files are supported")
        else:
            # Fallback to file extension check
            if file.filename and file.filename.lower().endswith('.pdf'):
                return await process_pdf_upload(patient_id, file)
            elif file.filename and any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']):
                return await process_image_upload(patient_id, file)
            else:
                raise HTTPException(status_code=400, detail="Only PDF and image files are supported")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing patient history: {str(e)}")

async def process_pdf_upload(patient_id: str, file: UploadFile):
    """Process PDF upload."""
        # Process PDF and extract medical information
    medical_data = await pdf_service.process_medical_pdf(file)
    # Store in vector database
    await memory_service.store_patient_history(patient_id, medical_data)
    return {
        "message": "Patient history uploaded successfully",
        "patient_id": patient_id,
        "extracted_data": medical_data,
        "full_text": medical_data.get("full_text", ""),
        "file_type": "PDF"
    }

async def process_image_upload(patient_id: str, file: UploadFile):
    """Process image upload with OCR."""
    # Extract text from image using OCR
    ocr_result = await ocr_service.extract_text_from_image(file)
    
    # Convert image to PDF for consistency
    pdf_content = await ocr_service.convert_image_to_pdf(file)
    
    # Create a mock UploadFile with PDF content for processing
    from io import BytesIO
    filename = file.filename or "uploaded_image.pdf"
    pdf_filename = filename.replace('.jpg', '.pdf').replace('.jpeg', '.pdf').replace('.png', '.pdf')
    if not pdf_filename.endswith('.pdf'):
        pdf_filename += '.pdf'
    
    pdf_file = UploadFile(
        filename=pdf_filename,
        file=BytesIO(pdf_content)
    )
    pdf_file.content_type = 'application/pdf'
    
    # Process the extracted text as if it were a PDF
    medical_data = await pdf_service.process_medical_pdf(pdf_file)
        
        # Store in vector database
    await memory_service.store_patient_history(patient_id, medical_data)
        
    return {
        "message": "Patient history uploaded successfully (OCR processed)",
            "patient_id": patient_id,
        "extracted_data": medical_data,
        "full_text": medical_data.get("full_text", ""),
        "ocr_result": ocr_result,
        "file_type": "Image"
        }

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
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

# User-friendly image analysis endpoint
@app.post("/api/analyze-image")
async def analyze_image_with_user(
    patient_id: str = Form(...),
    image: UploadFile = File(...),
    image_type: str = Form("skin")
):
    """User-friendly image analysis endpoint with patient context."""
    try:
        if image.content_type and not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Analyze image
        analysis_result = await image_service.analyze_medical_image(
            image_file=image,
            image_type=image_type
        )
        
        # Store in memory
        await memory_service.store_image_analysis(patient_id, analysis_result)
        
        return {
            "message": "Image analysis completed successfully",
            "patient_id": patient_id,
            "analysis": analysis_result
        }
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

@app.post("/speech-to-symptoms")
async def convert_speech_to_symptoms(
    patient_id: Optional[str] = Form(None),
    audio: UploadFile = File(...)
):
    """
    Convert speech input to symptoms text with extraction
    """
    try:
        if audio.content_type and not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Only audio files are supported")
        
        # Process speech to symptoms using the enhanced service
        result = await speech_service.process_speech_to_symptoms(audio)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Speech processing failed: {result.get('error', 'Unknown error')}")
        
        # Get the transcribed text and extracted symptoms
        transcribed_text = result["transcription"]["transcribed_text"]
        symptoms_data = result["symptoms"]
        
        # Analyze the extracted symptoms if any were found
        diagnosis = None
        if symptoms_data["all_symptoms"]:
            # Use the original transcribed text for analysis
            diagnosis = await symptom_checker.analyze_symptoms(
            symptoms=transcribed_text,
            patient_history=None,
            severity_level=SeverityLevel.MEDIUM
        )
        
        return {
            "transcription": result["transcription"],
            "extracted_symptoms": symptoms_data,
            "diagnosis": diagnosis,
            "success": True
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

# User Authentication Endpoints
@app.post("/api/auth/register", response_model=UserProfile)
async def register_user(user_data: UserRegistration):
    """Register a new user with auto-generated patient ID."""
    try:
        user_profile = await user_service.register_user(user_data)
        return user_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login", response_model=UserProfile)
async def login_user(login_data: UserLogin):
    """Authenticate user and return profile."""
    try:
        user_profile = await user_service.login_user(login_data)
        return user_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/user/profile/{patient_id}", response_model=UserProfile)
async def get_user_profile(patient_id: str):
    """Get user profile by patient ID."""
    try:
        user_profile = await user_service.get_user_profile(patient_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        return user_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@app.put("/api/user/profile/{patient_id}", response_model=UserProfile)
async def update_user_profile(patient_id: str, profile_data: dict):
    """Update user profile information."""
    try:
        updated_profile = await user_service.update_user_profile(patient_id, profile_data)
        return updated_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# Dashboard Endpoints
@app.get("/api/dashboard/{patient_id}", response_model=UserDashboard)
async def get_dashboard_data(patient_id: str):
    """Get comprehensive dashboard data for user."""
    try:
        dashboard_data = await user_service.get_dashboard_data(patient_id)
        return dashboard_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@app.get("/api/documents/{patient_id}")
async def get_user_documents(patient_id: str, limit: int = 10):
    """Get user's uploaded documents."""
    try:
        documents = await user_service.get_user_documents(patient_id, limit)
        return {"documents": [doc.dict() for doc in documents]}
    except Exception as e:
        logger.error(f"Document retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")

# Enhanced Upload Endpoint with User Integration
@app.post("/api/upload/{patient_id}")
async def upload_patient_history_with_user(
    patient_id: str,
    file: UploadFile = File(...),
    patient_id_form: str = Form(...)
):
    """Upload patient history (PDF or image) with user integration."""
    if patient_id != patient_id_form:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        file.file.seek(0)  # Reset pointer
        
        # Process based on file type
        if file_extension == 'pdf':
            # Process PDF directly
            extracted_data = await pdf_service.process_medical_pdf(file)
            full_text = extracted_data.get('full_text', '')
            file_type = 'PDF'
        else:
            # Process image with OCR
            extracted_data = await ocr_service.extract_text_from_image(file)
            full_text = extracted_data.get('full_text', '')
            file_type = 'Image'
        
        # Save document to user's account
        document = await user_service.save_document(
            patient_id=patient_id,
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            extracted_data=extracted_data,
            full_text=full_text
        )
        # Also store in memory service for similarity search
        await memory_service.store_patient_history(patient_id, extracted_data)
        return {
            "message": "File uploaded and processed successfully",
            "patient_id": patient_id,
            "document_id": document.document_id,
            "filename": file.filename,
            "file_type": file_type,
            "file_size": file_size,
            "extracted_data": extracted_data,
            "full_text": full_text,
            "upload_date": document.upload_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

# Symptom Checker Endpoint (Enhanced)
@app.post("/api/check-symptoms")
async def check_symptoms(
    request: SymptomRequest,
    patient_id: str = Form(...)
):
    """Check symptoms with user context."""
    try:
        # Get user profile for context
        user_profile = await user_service.get_user_profile(patient_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Process symptoms with user context
        response = await symptom_checker.analyze_symptoms(
            symptoms=request.symptoms,
            patient_history=None,  # Will be fetched by the service
            severity_level=request.severity_level,
            similar_cases=[]  # Will be fetched by the service
        )
        # Save diagnosis to user history
        try:
            await user_service.save_user_diagnosis(patient_id, request.symptoms, response.dict())
        except Exception as e:
            logger.warning(f"Failed to save diagnosis for user: {e}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Symptom check error: {e}")
        raise HTTPException(status_code=500, detail="Symptom check failed")

# Legacy endpoint for backward compatibility
@app.post("/api/upload")
async def upload_patient_history_legacy(
    file: UploadFile = File(...),
    patient_id: str = Form(...)
):
    """Legacy upload endpoint for backward compatibility."""
    return await upload_patient_history_with_user(patient_id, file, patient_id)

# Speech-to-Symptoms Endpoint with User Authentication
@app.post("/api/speech-to-symptoms")
async def convert_speech_to_symptoms_with_user(
    patient_id: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Convert speech input to symptoms with user authentication
    """
    try:
        if audio.content_type and not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Only audio files are supported")
        
        # Process speech to symptoms
        result = await speech_service.process_speech_to_symptoms(audio)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Speech processing failed: {result.get('error', 'Unknown error')}")
        
        # Get the transcribed text and extracted symptoms
        transcribed_text = result["transcription"]["transcribed_text"]
        symptoms_data = result["symptoms"]
        
        # Get patient history for context
        patient_history = None
        if patient_id:
            patient_history = await memory_service.get_patient_history(patient_id)
        
        # Analyze the extracted symptoms if any were found
        diagnosis = None
        if symptoms_data["all_symptoms"]:
            diagnosis = await symptom_checker.analyze_symptoms(
                symptoms=transcribed_text,
                patient_history=patient_history,
                severity_level=SeverityLevel.MEDIUM
            )
        
        return {
            "patient_id": patient_id,
            "transcription": result["transcription"],
            "extracted_symptoms": symptoms_data,
            "diagnosis": diagnosis,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing speech: {str(e)}")

@app.delete("/api/documents/{patient_id}/{document_id}")
async def delete_user_document(patient_id: str, document_id: str):
    """Delete a user's document by document_id."""
    try:
        await user_service.delete_user_document(patient_id, document_id)
        return {"message": "Document deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
