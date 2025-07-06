import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio

from models.symptom_models import SymptomRequest, DiagnosisResponse, PatientHistory, SeverityLevel

class SymptomCheckerService:
    """Core service for analyzing symptoms using AI models"""
    
    def __init__(self):
        # Initialize Google Gemini
        self.gemini_model = None
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # Use a supported model name; check the docs or your account for available models
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.0-pro', etc.
        
        # Medical knowledge base for symptom-disease mapping
        self.symptom_database = self._load_symptom_database()
    
    def _load_symptom_database(self) -> Dict[str, Any]:
        """Load medical symptom-disease database"""
        # This would typically load from a comprehensive medical database
        # For now, using a simplified version
        return {
            "respiratory": {
                "symptoms": ["cough", "shortness of breath", "chest pain", "fever", "fatigue"],
                "conditions": ["common cold", "flu", "pneumonia", "bronchitis", "asthma"]
            },
            "cardiovascular": {
                "symptoms": ["chest pain", "shortness of breath", "dizziness", "palpitations"],
                "conditions": ["angina", "heart attack", "arrhythmia", "hypertension"]
            },
            "gastrointestinal": {
                "symptoms": ["nausea", "vomiting", "abdominal pain", "diarrhea", "constipation"],
                "conditions": ["gastritis", "food poisoning", "appendicitis", "ulcer"]
            },
            "neurological": {
                "symptoms": ["headache", "dizziness", "numbness", "seizures", "memory loss"],
                "conditions": ["migraine", "stroke", "epilepsy", "concussion"]
            },
            "dermatological": {
                "symptoms": ["rash", "itching", "redness", "swelling", "blisters"],
                "conditions": ["eczema", "psoriasis", "allergic reaction", "infection"]
            }
        }
    
    async def analyze_symptoms(
        self, 
        symptoms: str, 
        patient_history: Optional[PatientHistory] = None,
        severity_level: SeverityLevel = SeverityLevel.MEDIUM,
        similar_cases: Optional[list] = None
    ) -> DiagnosisResponse:
        """
        Analyze symptoms and provide diagnosis suggestions, using similar cases for context if available
        """
        try:
            # Create context with patient history and similar cases
            context = self._build_context(symptoms, patient_history, severity_level, similar_cases)
            
            # Use LLM for analysis
            diagnosis_result = await self._get_llm_analysis(context)
            
            # Enhance with medical database lookup
            enhanced_result = self._enhance_with_medical_database(symptoms, diagnosis_result)
            
            return enhanced_result
            
        except Exception as e:
            # Fallback to basic analysis
            return self._fallback_analysis(symptoms, severity_level)
    
    def _build_context(
        self, 
        symptoms: str, 
        patient_history: Optional[PatientHistory],
        severity_level: SeverityLevel,
        similar_cases: Optional[list] = None
    ) -> str:
        """Build context for LLM analysis, including similar cases if provided"""
        context = f"""
        Patient Symptoms: {symptoms}
        Perceived Severity: {severity_level.value}
        """
        if patient_history:
            context += f"""
            Patient History:
            - Medical Conditions: {', '.join(patient_history.medical_conditions)}
            - Medications: {', '.join(patient_history.medications)}
            - Allergies: {', '.join(patient_history.allergies)}
            - Past Surgeries: {', '.join(patient_history.surgeries)}
            """
        if similar_cases:
            context += "\nSimilar Medical Cases:"
            for case in similar_cases:
                context += f"\n- Case: {case.symptoms} | Diagnosis: {case.diagnosis} | Outcome: {case.outcome}"
        context += """
        \nMedical Analysis Task:
        1. Analyze the symptoms provided
        2. Consider patient history and similar cases if available
        3. Provide probable diagnoses with confidence levels
        4. Assess severity and urgency
        5. Recommend appropriate actions and tests
        6. Include medical disclaimers
        \nPlease provide a structured response in JSON format with the following fields:
        - probable_diagnoses: list of diagnoses with confidence scores
        - severity_assessment: low/medium/high/critical
        - recommended_actions: list of actions
        - suggested_tests: list of medical tests
        - urgency_level: immediate/within_hours/within_days/routine
        - confidence_score: 0.0 to 1.0
        - disclaimer: medical disclaimer
        """
        return context
    
    async def _get_llm_analysis(self, context: str) -> Dict[str, Any]:
        """Get analysis from LLM (Google Gemini)"""
        try:
            if self.gemini_model:
                try:
                    gemini_prompt = f"""
                    You are a medical AI assistant. Analyze the following patient information and provide a structured medical assessment.

                    {context}

                    IMPORTANT: Respond with ONLY valid JSON in the following format:
                    {{
                        "probable_diagnoses": [
                            {{"condition": "condition_name", "confidence": 0.8}}
                        ],
                        "severity_assessment": "low/medium/high/critical",
                        "recommended_actions": ["action1", "action2"],
                        "suggested_tests": ["test1", "test2"],
                        "urgency_level": "immediate/within_hours/within_days/routine",
                        "confidence_score": 0.7,
                        "disclaimer": "Medical disclaimer text"
                    }}
                    """
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        gemini_prompt
                    )
                    result_text = response.text or ""
                    return self._parse_llm_response(result_text)
                except Exception as gemini_error:
                    print(f"Gemini analysis failed: {gemini_error}")
            raise Exception("No Gemini API key configured or Gemini model unavailable")
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return {}
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to extract JSON from response
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._extract_structured_data(response_text)
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
            return {}
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from unstructured LLM response"""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        result = {
            "probable_diagnoses": [],
            "severity_assessment": "medium",
            "recommended_actions": [],
            "suggested_tests": [],
            "urgency_level": "within_days",
            "confidence_score": 0.6,
            "disclaimer": "This is not a substitute for professional medical advice."
        }
        
        # Extract diagnoses (simplified)
        if "diagnosis" in text.lower() or "condition" in text.lower():
            result["probable_diagnoses"] = [
                {"condition": "General assessment", "confidence": 0.6}
            ]
        
        # Extract severity
        if "severe" in text.lower() or "critical" in text.lower():
            result["severity_assessment"] = "high"
        elif "mild" in text.lower():
            result["severity_assessment"] = "low"
        
        return result
    
    def _enhance_with_medical_database(self, symptoms: str, llm_result: Dict[str, Any]) -> DiagnosisResponse:
        """Enhance LLM results with medical database lookup"""
        # Analyze symptoms against our database
        detected_categories = []
        for category, data in self.symptom_database.items():
            for symptom in data["symptoms"]:
                if symptom.lower() in symptoms.lower():
                    detected_categories.append(category)
                    break
        
        # Add database-based diagnoses
        if detected_categories and not llm_result.get("probable_diagnoses"):
            for category in detected_categories:
                conditions = self.symptom_database[category]["conditions"]
                for condition in conditions[:2]:  # Top 2 conditions per category
                    llm_result.setdefault("probable_diagnoses", []).append({
                        "condition": condition,
                        "confidence": 0.5,
                        "source": "medical_database"
                    })
        
        return DiagnosisResponse(
            probable_diagnoses=llm_result.get("probable_diagnoses", []),
            severity_assessment=llm_result.get("severity_assessment", "medium"),
            recommended_actions=llm_result.get("recommended_actions", ["Consult a healthcare provider"]),
            suggested_tests=llm_result.get("suggested_tests", []),
            urgency_level=llm_result.get("urgency_level", "within_days"),
            confidence_score=llm_result.get("confidence_score", 0.5),
            disclaimer=llm_result.get("disclaimer", "This analysis is for informational purposes only and should not replace professional medical advice.")
        )
    
    def _fallback_analysis(self, symptoms: str, severity_level: SeverityLevel) -> DiagnosisResponse:
        """Fallback analysis when LLM is unavailable"""
        return DiagnosisResponse(
            probable_diagnoses=[
                {"condition": "Symptom assessment", "confidence": 0.3}
            ],
            severity_assessment=severity_level.value,
            recommended_actions=[
                "Consult a healthcare provider for proper diagnosis",
                "Monitor symptoms for changes",
                "Seek emergency care if symptoms worsen"
            ],
            suggested_tests=["Physical examination by healthcare provider"],
            urgency_level="within_days",
            confidence_score=0.3,
            disclaimer="This is a basic symptom assessment. Please consult a healthcare professional for proper medical evaluation."
        )
    
    async def get_symptom_categories(self) -> List[str]:
        """Get available symptom categories"""
        return list(self.symptom_database.keys())
    
    async def search_similar_cases(self, symptoms: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar medical cases (placeholder for vector search)"""
        # This would integrate with vector database
        return [
            {
                "case_id": "case_001",
                "symptoms": "Similar symptoms",
                "diagnosis": "Example diagnosis",
                "similarity_score": 0.8
            }
        ] 