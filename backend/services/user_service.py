import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
import logging

from models.user_models import UserRegistration, UserLogin, UserProfile, UserDocument, UserDashboard, generate_patient_id, generate_document_id

logger = logging.getLogger(__name__)

class UserService:
    """Service for user management, authentication, and document storage."""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.documents_file = "data/documents.json"
        self.sessions_file = "data/sessions.json"
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("uploads", exist_ok=True)
        
        # Initialize data files
        self._init_data_files()
    
    def _init_data_files(self):
        """Initialize JSON data files if they don't exist."""
        files = [self.users_file, self.documents_file, self.sessions_file]
        for file_path in files:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return self._hash_password(password) == hashed
    
    def _load_data(self, file_path: str) -> dict:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return {}
    
    def _save_data(self, file_path: str, data: dict):
        """Save data to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
    
    async def register_user(self, user_data: UserRegistration) -> UserProfile:
        """Register a new user with auto-generated patient ID."""
        users = self._load_data(self.users_file)
        
        # Check if email already exists
        for user in users.values():
            if user.get('email') == user_data.email:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate patient ID
        patient_id = generate_patient_id()
        
        # Create user profile
        user_profile = UserProfile(
            patient_id=patient_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            age=user_data.age,
            gender=user_data.gender,
            chronic_conditions=user_data.chronic_conditions or [],
            created_at=datetime.now()
        )
        
        # Store user data
        users[patient_id] = {
            **user_profile.dict(),
            'password_hash': self._hash_password(user_data.password)
        }
        
        self._save_data(self.users_file, users)
        
        # Create user upload directory
        user_upload_dir = f"uploads/{patient_id}"
        os.makedirs(user_upload_dir, exist_ok=True)
        
        logger.info(f"User registered: {patient_id}")
        return user_profile
    
    async def login_user(self, login_data: UserLogin) -> UserProfile:
        """Authenticate user and return profile."""
        users = self._load_data(self.users_file)
        
        # Find user by email
        user_data = None
        patient_id = None
        for pid, user in users.items():
            if user.get('email') == login_data.email:
                user_data = user
                patient_id = pid
                break
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not self._verify_password(login_data.password, user_data['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last login
        user_data['last_login'] = datetime.now().isoformat()
        users[patient_id] = user_data
        self._save_data(self.users_file, users)
        
        # Return user profile (without password)
        return UserProfile(**{k: v for k, v in user_data.items() if k != 'password_hash'})
    
    async def get_user_profile(self, patient_id: str) -> Optional[UserProfile]:
        """Get user profile by patient ID."""
        users = self._load_data(self.users_file)
        user_data = users.get(patient_id)
        
        if not user_data:
            return None
        
        return UserProfile(**{k: v for k, v in user_data.items() if k != 'password_hash'})
    
    async def save_document(self, patient_id: str, filename: str, file_type: str, 
                           file_size: int, extracted_data: dict, full_text: str) -> UserDocument:
        """Save uploaded document information."""
        documents = self._load_data(self.documents_file)
        
        document_id = generate_document_id()
        
        document = UserDocument(
            document_id=document_id,
            patient_id=patient_id,
            filename=filename,
            file_type=file_type,
            upload_date=datetime.now(),
            file_size=file_size,
            extracted_data=extracted_data,
            full_text=full_text,
            confidence_score=extracted_data.get('extraction_confidence', 0.0)
        )
        
        # Store document data
        if patient_id not in documents:
            documents[patient_id] = []
        
        documents[patient_id].append(document.dict())
        self._save_data(self.documents_file, documents)
        
        logger.info(f"Document saved: {document_id} for patient {patient_id}")
        return document
    
    async def get_user_documents(self, patient_id: str, limit: int = 10) -> List[UserDocument]:
        """Get user's uploaded documents."""
        documents = self._load_data(self.documents_file)
        user_docs = documents.get(patient_id, [])
        
        # Sort by upload date (newest first) and limit
        sorted_docs = sorted(user_docs, key=lambda x: x.get('upload_date', ''), reverse=True)[:limit]
        
        return [UserDocument(**doc) for doc in sorted_docs]
    
    async def get_dashboard_data(self, patient_id: str) -> UserDashboard:
        """Get comprehensive dashboard data for user."""
        # Get user profile
        user_profile = await self.get_user_profile(patient_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent documents
        recent_documents = await self.get_user_documents(patient_id, limit=5)
        
        # Get total document count
        documents = self._load_data(self.documents_file)
        total_documents = len(documents.get(patient_id, []))
        
        # Create health summary (placeholder for now)
        health_summary = {
            "total_uploads": total_documents,
            "last_upload": recent_documents[0].upload_date if recent_documents else None,
            "extraction_confidence_avg": sum(doc.confidence_score for doc in recent_documents) / len(recent_documents) if recent_documents else 0
        }
        
        return UserDashboard(
            patient_id=patient_id,
            user_info=user_profile,
            total_documents=total_documents,
            recent_documents=recent_documents,
            recent_diagnoses=[],  # Placeholder for symptom check history
            health_summary=health_summary
        )
    
    async def update_user_profile(self, patient_id: str, profile_data: dict) -> UserProfile:
        """Update user profile information."""
        users = self._load_data(self.users_file)
        user_data = users.get(patient_id)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'age', 'gender', 'chronic_conditions']
        for field in allowed_fields:
            if field in profile_data:
                user_data[field] = profile_data[field]
        
        users[patient_id] = user_data
        self._save_data(self.users_file, users)
        
        return UserProfile(**{k: v for k, v in user_data.items() if k != 'password_hash'})
    
    async def delete_user_document(self, patient_id: str, document_id: str) -> bool:
        """Delete a user's document by document_id."""
        documents = self._load_data(self.documents_file)
        user_docs = documents.get(patient_id, [])
        new_docs = [doc for doc in user_docs if doc.get('document_id') != document_id]
        if len(new_docs) == len(user_docs):
            raise HTTPException(status_code=404, detail="Document not found")
        documents[patient_id] = new_docs
        self._save_data(self.documents_file, documents)
        # Optionally, delete the file from uploads directory
        user_upload_dir = f"uploads/{patient_id}"
        for ext in ['.pdf', '.jpg', '.jpeg', '.png']:
            file_path = os.path.join(user_upload_dir, f"{document_id}{ext}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete file {file_path}: {e}")
        logger.info(f"Deleted document {document_id} for patient {patient_id}")
        return True 