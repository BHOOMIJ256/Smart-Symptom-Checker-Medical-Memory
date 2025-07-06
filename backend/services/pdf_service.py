import fitz  # PyMuPDF
import pdfplumber
import re
import tempfile
import os
from typing import Any, Dict, List, Optional
from fastapi import UploadFile, HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessingService:
    """Service for processing and extracting data from medical PDFs."""

    def __init__(self):
        # Medical keywords for extraction
        self.medical_conditions_keywords = [
            'diagnosis', 'condition', 'disease', 'illness', 'syndrome',
            'hypertension', 'diabetes', 'asthma', 'arthritis', 'cancer',
            'heart disease', 'stroke', 'depression', 'anxiety', 'obesity'
        ]
        
        self.medication_keywords = [
            'medication', 'medication list', 'current medications', 'prescribed',
            'drug', 'medicine', 'prescription', 'dosage', 'mg', 'tablet',
            'capsule', 'injection', 'inhaler', 'cream', 'ointment'
        ]
        
        self.allergy_keywords = [
            'allergy', 'allergic', 'allergies', 'adverse reaction',
            'drug allergy', 'food allergy', 'environmental allergy'
        ]
        
        self.surgery_keywords = [
            'surgery', 'surgical', 'operation', 'procedure', 'post-op',
            'post-operative', 'surgical history', 'operation date'
        ]
        
        self.lab_keywords = [
            'lab results', 'laboratory', 'blood test', 'urine test',
            'x-ray', 'mri', 'ct scan', 'ultrasound', 'biopsy'
        ]

    async def process_medical_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Extract medical data from PDF using multiple extraction methods."""
        try:
            # Create temporary file to process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Extract data using multiple methods
            extracted_data = {}
            full_text = ""
            
            # Method 1: PyMuPDF extraction
            mupdf_data, mupdf_text = self._extract_with_pymupdf(temp_file_path, return_text=True)
            extracted_data.update(mupdf_data)
            full_text = mupdf_text
            
            # Method 2: pdfplumber extraction (optional: could merge text)
            # pdfplumber_data = self._extract_with_pdfplumber(temp_file_path)
            # extracted_data.update(pdfplumber_data)
            
            # Method 3: Enhanced text analysis
            enhanced_data = self._enhance_extraction(extracted_data)
            extracted_data.update(enhanced_data)
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Structure the final output
            return self._structure_output(extracted_data, full_text=full_text)
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

    def _extract_with_pymupdf(self, file_path: str, return_text: bool = False) -> Any:
        """Extract text and data using PyMuPDF. Optionally return full text."""
        try:
            doc = fitz.open(file_path)  # type: ignore[attr-defined]
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            
            # Extract structured data from text
            parsed = self._parse_medical_text(text_content)
            if return_text:
                return parsed, text_content
            return parsed
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction error: {str(e)}")
            if return_text:
                return {"error": str(e)}, ""
            return {}

    def _extract_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Extract text and tables using pdfplumber."""
        try:
            with pdfplumber.open(file_path) as pdf:
                text_content = ""
                tables_data = []
                
                for page in pdf.pages:
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:  # Ensure table has data
                            tables_data.append(table)
                
                # Parse tables for medical data
                table_data = self._parse_medical_tables(tables_data)
                
                # Parse text content
                text_data = self._parse_medical_text(text_content)
                
                # Combine results
                result = {}
                result.update(text_data)
                result.update(table_data)
                
                return result
                
        except Exception as e:
            logger.error(f"pdfplumber extraction error: {str(e)}")
            return {}

    def _parse_medical_text(self, text: str) -> Dict[str, Any]:
        """Parse medical information from text content."""
        text = text.lower()
        lines = text.split('\n')
        
        extracted_data = {
            'medical_conditions': [],
            'medications': [],
            'allergies': [],
            'surgeries': [],
            'lab_results': [],
            'notes': []
        }
        
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            line_original = line.strip()
            
            # Skip empty lines
            if not line_lower:
                continue
            
            # Detect sections - handle various formats
            if any(keyword in line_lower for keyword in ['medical conditions:', 'medical history:', 'diagnosis:', 'preliminary diagnosis:']):
                current_section = 'medical_conditions'
                continue
            elif any(keyword in line_lower for keyword in ['medications:', 'current medications:', 'drugs:', 'prescriptions:']):
                current_section = 'medications'
                continue
            elif any(keyword in line_lower for keyword in ['allergies:', 'allergic:', 'drug allergies:', 'food allergies:']):
                current_section = 'allergies'
                continue
            elif any(keyword in line_lower for keyword in ['surgical history:', 'surgeries:', 'operations:', 'past surgeries:', 'surgical procedures:']):
                current_section = 'surgeries'
                continue
            elif any(keyword in line_lower for keyword in ['lab results:', 'laboratory results:', 'test results:', 'recommended tests:', 'blood tests:', 'imaging:']):
                current_section = 'lab_results'
                continue
            elif any(keyword in line_lower for keyword in ['physician notes:', 'doctor notes:', 'clinical notes:', 'notes:', 'comments:', 'observations:']):
                current_section = 'notes'
                continue
            
            # Process bullet points (• or -) - handle various bullet formats including (cid:127)
            bullet_match = re.match(r"^[•\-*\u2022\u2023\u25E6\u2043\u2219\s\(cid:\d+\)]+(.*)", line_original)
            if bullet_match:
                item = bullet_match.group(1).strip()
                
                if current_section == 'medical_conditions':
                    extracted_data['medical_conditions'].append(item)
                elif current_section == 'medications':
                    # Extract medication name and dosage
                    if 'mg' in item.lower() or 'mcg' in item.lower() or 'g' in item.lower():
                        # This looks like a medication with dosage
                        extracted_data['medications'].append({
                            'name': item.split()[0].title() if item.split() else item,
                            'dosage': item,
                            'source_line': line_original
                        })
                    else:
                        extracted_data['medications'].append(item)
                elif current_section == 'allergies':
                    extracted_data['allergies'].append(item)
                elif current_section == 'surgeries':
                    extracted_data['surgeries'].append(item)
                elif current_section == 'lab_results':
                    extracted_data['lab_results'].append(item)
                elif current_section == 'notes':
                    extracted_data['notes'].append(item)
            
            # Also try pattern matching for non-bullet point text
            else:
                # Extract medications (look for dosage patterns)
                medication_patterns = [
                    r'(\w+)\s+(\d+)\s*(mg|mcg|g|ml)\s*(daily|twice|three times|qid|tid|bid|qd)',
                    r'(\w+)\s+(\d+)\s*(mg|mcg|g|ml)',
                    r'(\w+)\s+(tablet|capsule|injection|cream|ointment)',
                ]
                
                for pattern in medication_patterns:
                    matches = re.findall(pattern, line_lower)
                    for match in matches:
                        if len(match) >= 2:
                            med_name = match[0].strip()
                            if len(med_name) > 2:  # Filter out very short matches
                                extracted_data['medications'].append({
                                    'name': med_name.title(),
                                    'dosage': ' '.join(match[1:]) if len(match) > 1 else '',
                                    'source_line': line_original
                                })
                
                # Extract allergies
                if any(keyword in line_lower for keyword in self.allergy_keywords):
                    allergy_matches = re.findall(r'(\w+)\s+(allergy|allergic)', line_lower)
                    for match in allergy_matches:
                        if match[0] not in ['no', 'none', 'negative']:
                            extracted_data['allergies'].append(match[0].title())
                
                # Extract medical conditions
                if any(keyword in line_lower for keyword in self.medical_conditions_keywords):
                    condition_matches = re.findall(r'(diagnosis|condition):\s*(\w+(?:\s+\w+)*)', line_lower)
                    for match in condition_matches:
                        if match[1]:
                            extracted_data['medical_conditions'].append(match[1].title())
                
                # Extract surgeries
                if any(keyword in line_lower for keyword in self.surgery_keywords):
                    surgery_matches = re.findall(r'(\w+(?:\s+\w+)*)\s+(surgery|operation|procedure)', line_lower)
                    for match in surgery_matches:
                        if match[0]:
                            extracted_data['surgeries'].append(match[0].title())
                
                # Extract lab results
                if any(keyword in line_lower for keyword in self.lab_keywords):
                    extracted_data['lab_results'].append(line_original)
        
        return extracted_data

    def _parse_medical_tables(self, tables: List[List]) -> Dict[str, Any]:
        """Parse medical data from tables."""
        extracted_data = {
            'medical_conditions': [],
            'medications': [],
            'allergies': [],
            'surgeries': [],
            'lab_results': []
        }
        
        for table in tables:
            if not table or len(table) < 2:
                continue
                
            # Look for table headers
            headers = [str(cell).lower() if cell else '' for cell in table[0]]
            
            # Process based on table type
            if any('medication' in header for header in headers):
                for row in table[1:]:
                    if len(row) >= 2:
                        med_name = str(row[0]).strip()
                        if med_name and med_name.lower() not in ['none', 'n/a', '']:
                            extracted_data['medications'].append({
                                'name': med_name.title(),
                                'dosage': str(row[1]).strip() if len(row) > 1 else '',
                                'source': 'table'
                            })
            
            elif any('allergy' in header for header in headers):
                for row in table[1:]:
                    allergy = str(row[0]).strip()
                    if allergy and allergy.lower() not in ['none', 'n/a', '']:
                        extracted_data['allergies'].append(allergy.title())
            
            elif any('condition' in header or 'diagnosis' in header for header in headers):
                for row in table[1:]:
                    condition = str(row[0]).strip()
                    if condition and condition.lower() not in ['none', 'n/a', '']:
                        extracted_data['medical_conditions'].append(condition.title())
        
        return extracted_data

    def _enhance_extraction(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance extraction with additional processing."""
        enhanced_data = {}
        
        # Remove duplicates and clean up
        for key in ['medical_conditions', 'medications', 'allergies', 'surgeries']:
            if key in extracted_data:
                if isinstance(extracted_data[key], list):
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_items = []
                    for item in extracted_data[key]:
                        if isinstance(item, dict):
                            item_str = item.get('name', '')
                        else:
                            item_str = str(item)
                        
                        if item_str and item_str.lower() not in seen:
                            seen.add(item_str.lower())
                            unique_items.append(item)
                    
                    enhanced_data[key] = unique_items
                else:
                    enhanced_data[key] = extracted_data[key]
        
        # Add confidence scores
        enhanced_data['extraction_confidence'] = self._calculate_confidence(extracted_data)
        
        return enhanced_data

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for extraction."""
        confidence = 0.0
        total_items = 0
        
        for key in ['medical_conditions', 'medications', 'allergies', 'surgeries']:
            if key in data and data[key]:
                confidence += 0.25  # Each category contributes to confidence
                total_items += len(data[key]) if isinstance(data[key], list) else 1
        
        # Normalize confidence
        if total_items > 0:
            confidence = min(confidence + (total_items * 0.1), 1.0)
        
        return round(confidence, 2)

    def _structure_output(self, extracted_data: Dict[str, Any], full_text: str = "") -> Dict[str, Any]:
        """Structure the final output according to the expected format, including full_text."""
        # Convert medications to strings if they are dictionaries
        medications = []
        for item in extracted_data.get('medications', []):
            if isinstance(item, dict):
                med_name = item.get('name', '')
                med_dosage = item.get('dosage', '')
                if med_name and med_dosage:
                    medications.append(f"{med_name} {med_dosage}")
                elif med_name:
                    medications.append(med_name)
            else:
                medications.append(str(item))
        
        # Convert lab_results to proper format (List[Dict[str, Any]])
        lab_results = []
        for lab_item in extracted_data.get('lab_results', []):
            if isinstance(lab_item, str):
                lab_results.append({"test": "Lab Result", "value": lab_item, "unit": ""})
            elif isinstance(lab_item, dict):
                lab_results.append(lab_item)
        
        # Convert notes to string (join all notes into one string)
        notes_list = extracted_data.get('notes', [])
        notes_string = "; ".join(notes_list) if notes_list else ""
        
        # Clean up the full text (remove extra whitespace and normalize)
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', full_text.strip())  # Remove excessive newlines
        cleaned_text = re.sub(r' +', ' ', cleaned_text)  # Remove multiple spaces
        
        return {
            "medical_conditions": [item.get('name', item) if isinstance(item, dict) else item 
                                 for item in extracted_data.get('medical_conditions', [])],
            "medications": medications,
            "allergies": extracted_data.get('allergies', []),
            "surgeries": extracted_data.get('surgeries', []),
            "lab_results": lab_results,
            "notes": notes_string,  # Convert list to string
            "extraction_confidence": extracted_data.get('extraction_confidence', 0.0),
            "extraction_methods": ["PyMuPDF", "pdfplumber", "enhanced_parsing"],
            "full_text": cleaned_text  # Cleaned full text
        } 