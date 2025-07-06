#!/usr/bin/env python3
"""
Test script for PDF extraction functionality.
This script helps you test the PDF extraction without needing to upload files through the API.
"""

import asyncio
import tempfile
import os
from services.pdf_service import PDFProcessingService
from fastapi import UploadFile
import io
from typing import Optional

class MockUploadFile(UploadFile):
    """Mock UploadFile for testing purposes."""
    def __init__(self, file_path: str, filename: Optional[str] = None):
        self.file_path = file_path
        self._filename = filename or os.path.basename(file_path)
        self._content_type = "application/pdf"
        self._file = None
    
    @property
    def filename(self) -> str:
        return self._filename
    
    @property
    def content_type(self) -> str:
        return self._content_type
    
    async def read(self) -> bytes:
        with open(self.file_path, 'rb') as f:
            return f.read()
    
    async def seek(self, offset: int) -> None:
        pass
    
    async def close(self) -> None:
        pass

def create_sample_pdf():
    """Create a sample PDF with medical data for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            pdf_path = temp_file.name
        
        # Create PDF content
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Add medical data to PDF
        y_position = height - 50
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y_position, "Patient Medical History")
        y_position -= 30
        
        # Medical Conditions
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Medical Conditions:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        conditions = ["Hypertension", "Type 2 Diabetes", "Asthma"]
        for condition in conditions:
            c.drawString(70, y_position, f"• {condition}")
            y_position -= 15
        
        # Medications
        y_position -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Current Medications:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        medications = [
            "Amlodipine 5mg daily",
            "Metformin 500mg twice daily",
            "Albuterol inhaler as needed"
        ]
        for med in medications:
            c.drawString(70, y_position, f"• {med}")
            y_position -= 15
        
        # Allergies
        y_position -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Allergies:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        allergies = ["Penicillin", "Sulfa drugs"]
        for allergy in allergies:
            c.drawString(70, y_position, f"• {allergy}")
            y_position -= 15
        
        # Surgeries
        y_position -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Surgical History:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        surgeries = ["Appendectomy (2015)", "Cataract surgery (2020)"]
        for surgery in surgeries:
            c.drawString(70, y_position, f"• {surgery}")
            y_position -= 15
        
        # Lab Results
        y_position -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Recent Lab Results:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        lab_results = [
            "Blood glucose: 120 mg/dL",
            "HbA1c: 6.8%",
            "Blood pressure: 140/90 mmHg"
        ]
        for result in lab_results:
            c.drawString(70, y_position, f"• {result}")
            y_position -= 15
        
        c.save()
        return pdf_path
        
    except ImportError:
        print("reportlab not available. Creating a simple text file instead.")
        # Create a simple text file as fallback
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            content = """
Patient Medical History

Medical Conditions:
• Hypertension
• Type 2 Diabetes
• Asthma

Current Medications:
• Amlodipine 5mg daily
• Metformin 500mg twice daily
• Albuterol inhaler as needed

Allergies:
• Penicillin
• Sulfa drugs

Surgical History:
• Appendectomy (2015)
• Cataract surgery (2020)

Recent Lab Results:
• Blood glucose: 120 mg/dL
• HbA1c: 6.8%
• Blood pressure: 140/90 mmHg
            """
            temp_file.write(content.encode())
            return temp_file.name

async def test_pdf_extraction():
    """Test the PDF extraction functionality."""
    print("Testing PDF Extraction Service...")
    print("=" * 50)
    
    # Create PDF service
    pdf_service = PDFProcessingService()
    
    # Create sample PDF
    print("Creating sample PDF with medical data...")
    pdf_path = create_sample_pdf()
    
    try:
        # Create mock upload file
        mock_file = MockUploadFile(pdf_path)
        
        # Process the PDF
        print("Extracting medical data from PDF...")
        result = await pdf_service.process_medical_pdf(mock_file)
        
        # Display results
        print("\nExtraction Results:")
        print("-" * 30)
        
        print(f"Medical Conditions: {result.get('medical_conditions', [])}")
        print(f"Medications: {result.get('medications', [])}")
        print(f"Allergies: {result.get('allergies', [])}")
        print(f"Surgeries: {result.get('surgeries', [])}")
        print(f"Lab Results: {result.get('lab_results', [])}")
        print(f"Extraction Confidence: {result.get('extraction_confidence', 0.0)}")
        print(f"Extraction Methods: {result.get('extraction_methods', [])}")
        
        # Show raw data for debugging
        print("\nRaw Extracted Data:")
        print("-" * 30)
        raw_data = result.get('raw_extracted_data', {})
        for key, value in raw_data.items():
            if value:  # Only show non-empty values
                print(f"{key}: {value}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
    
    finally:
        # Clean up
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

if __name__ == "__main__":
    asyncio.run(test_pdf_extraction()) 