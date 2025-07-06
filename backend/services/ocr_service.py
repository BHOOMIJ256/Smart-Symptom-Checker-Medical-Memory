import pytesseract
from PIL import Image
import io
import tempfile
import os
from typing import Any, Dict
from fastapi import UploadFile, HTTPException
import logging

# Configure logging
logger = logging.getLogger(__name__)

class OCRService:
    """Service for extracting text from images using OCR (Optical Character Recognition)."""
    
    def __init__(self):
        # Configure Tesseract path if needed (for Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    async def extract_text_from_image(self, image_file: UploadFile) -> Dict[str, Any]:
        """Extract text from an uploaded image using OCR."""
        try:
            # Read the image file
            content = await image_file.read()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(content))
            
            # Perform OCR
            extracted_text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            cleaned_text = self._clean_ocr_text(extracted_text)
            
            return {
                "extracted_text": cleaned_text,
                "confidence": "medium",  # Tesseract doesn't provide confidence scores by default
                "image_format": image.format,
                "image_size": image.size,
                "ocr_method": "Tesseract"
            }
            
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean and normalize OCR extracted text."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # Common OCR mistake in certain contexts
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    async def convert_image_to_pdf(self, image_file: UploadFile) -> bytes:
        """Convert an image to PDF format for consistency."""
        try:
            # Read the image file
            content = await image_file.read()
            
            # Open image with PIL
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary (PDF requires RGB)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                # Save as PDF
                image.save(temp_file.name, 'PDF')
                
                # Read the PDF content
                with open(temp_file.name, 'rb') as f:
                    pdf_content = f.read()
                
                # Clean up
                os.unlink(temp_file.name)
                
                return pdf_content
                
        except Exception as e:
            logger.error(f"Image to PDF conversion error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error converting image to PDF: {str(e)}") 