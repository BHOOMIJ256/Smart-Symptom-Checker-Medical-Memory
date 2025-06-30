#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly
"""

def test_imports():
    """Test all imports to ensure no issues"""
    try:
        # Test FastAPI imports
        from fastapi import FastAPI, HTTPException, UploadFile, File, Form
        print("✓ FastAPI imports successful")
        
        # Test our models
        from models.symptom_models import (
            SymptomRequest, 
            DiagnosisResponse, 
            PatientHistory, 
            SeverityLevel
        )
        print("✓ Model imports successful")
        
        # Test our services
        from services.symptom_checker import SymptomCheckerService
        from services.memory_service import MedicalMemoryService
        from services.image_service import ImageAnalysisService
        from services.speech_service import SpeechToTextService
        from services.pdf_service import PDFProcessingService
        print("✓ Service imports successful")
        
        # Test environment handling
        import os
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✓ dotenv import successful")
        except ImportError:
            print("⚠ dotenv not available, using fallback")
        
        print("\n🎉 All imports successful! No problems detected.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports() 