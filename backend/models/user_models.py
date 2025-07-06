from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

class UserRegistration(BaseModel):
    """Model for user registration"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    phone: Optional[str] = Field(None, description="User phone number")
    age: Optional[int] = Field(None, ge=0, le=120, description="User age")
    gender: Optional[str] = Field(None, description="User gender")
    chronic_conditions: Optional[List[str]] = Field(default=[], description="Known chronic conditions")

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserProfile(BaseModel):
    """Model for user profile"""
    patient_id: str = Field(..., description="Unique patient identifier")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    phone: Optional[str] = Field(None, description="User phone number")
    age: Optional[int] = Field(None, description="User age")
    gender: Optional[str] = Field(None, description="User gender")
    chronic_conditions: List[str] = Field(default=[], description="Known chronic conditions")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class UserDocument(BaseModel):
    """Model for user uploaded documents"""
    document_id: str = Field(..., description="Unique document identifier")
    patient_id: str = Field(..., description="Patient identifier")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (PDF, Image, etc.)")
    upload_date: datetime = Field(default_factory=datetime.now, description="Upload timestamp")
    file_size: int = Field(..., description="File size in bytes")
    extracted_data: dict = Field(default={}, description="Extracted medical data")
    full_text: str = Field(default="", description="Full extracted text")
    confidence_score: float = Field(default=0.0, description="Extraction confidence")

class UserDashboard(BaseModel):
    """Model for user dashboard data"""
    patient_id: str = Field(..., description="Patient identifier")
    user_info: UserProfile = Field(..., description="User profile information")
    total_documents: int = Field(default=0, description="Total uploaded documents")
    recent_documents: List[UserDocument] = Field(default=[], description="Recent uploads")
    recent_diagnoses: List[dict] = Field(default=[], description="Recent symptom checks")
    health_summary: dict = Field(default={}, description="Health summary data")

def generate_patient_id() -> str:
    """Generate a unique patient ID"""
    return f"P{uuid.uuid4().hex[:8].upper()}"

def generate_document_id() -> str:
    """Generate a unique document ID"""
    return f"D{uuid.uuid4().hex[:8].upper()}" 