import whisper
import tempfile
import os
import logging
from fastapi import UploadFile
from typing import Dict, Any, List
import re
import torch
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Service for converting speech audio to text and extracting symptoms."""
    
    def __init__(self):
        """Initialize the speech service with Whisper model."""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model with error handling."""
        try:
            # Check if CUDA is available, otherwise use CPU
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load Whisper model (will download on first use)
            logger.info("Loading Whisper model...")
            self.model = whisper.load_model("base", device=device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def retry_load_model(self):
        """Retry loading the model if it failed initially."""
        if self.model is None:
            logger.info("Retrying to load Whisper model...")
            self._load_model()
            return self.model is not None
        return True
    
    async def speech_to_text(self, audio: UploadFile) -> Dict[str, Any]:
        """
        Convert speech audio to text using OpenAI Whisper.
        
        Args:
            audio: UploadFile containing audio data
            
        Returns:
            Dict containing transcribed text and confidence score
        """
        # Try to load model if not loaded
        if not self.model:
            if not self.retry_load_model():
                raise Exception("Whisper model not loaded. Please restart the backend.")
        
        # Ensure model is loaded
        if not self.model:
            raise Exception("Whisper model not loaded. Please restart the backend.")
        
        temp_file_path = None
        try:
            # Create temporary file for audio with proper extension
            audio_content = await audio.read()
            
            # Determine file extension based on content type
            file_extension = ".wav"
            if audio.content_type:
                if "mp3" in audio.content_type:
                    file_extension = ".mp3"
                elif "m4a" in audio.content_type:
                    file_extension = ".m4a"
                elif "ogg" in audio.content_type:
                    file_extension = ".ogg"
                elif "webm" in audio.content_type:
                    file_extension = ".webm"
            
            # Create temporary file with proper extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name
            
            # Ensure file exists and has content
            if not os.path.exists(temp_file_path):
                raise Exception("Failed to create temporary audio file")
            
            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                raise Exception("Audio file is empty")
            
            logger.info(f"Audio file created: {temp_file_path} (size: {file_size} bytes)")
            
            # If the file is webm, convert to wav for Whisper
            if file_extension == ".webm":
                try:
                    audio_segment = AudioSegment.from_file(temp_file_path, format="webm")
                    wav_temp_file_path = temp_file_path + ".wav"
                    audio_segment.export(wav_temp_file_path, format="wav")
                    logger.info(f"Converted webm to wav: {wav_temp_file_path}")
                    # Remove the original webm temp file
                    os.unlink(temp_file_path)
                    temp_file_path = wav_temp_file_path
                except Exception as e:
                    logger.error(f"Failed to convert webm to wav: {e}")
                    raise Exception("Audio conversion error: " + str(e))
            
            # Transcribe audio using Whisper
            logger.info(f"Transcribing audio file: {temp_file_path}")
            result = self.model.transcribe(temp_file_path)
            
            # Handle the result properly
            text_result = result.get("text", "")
            transcribed_text = text_result.strip() if isinstance(text_result, str) else ""
            confidence = result.get("confidence", 0.0)
            
            logger.info(f"Transcription completed: {len(transcribed_text)} characters")
            
            return {
                "transcribed_text": transcribed_text,
                "confidence": confidence,
                "language": result.get("language", "en")
            }
                
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
    
    def extract_symptoms(self, text: str) -> Dict[str, Any]:
        """
        Extract symptoms from transcribed text using pattern matching and NLP.
        
        Args:
            text: Transcribed text from speech
            
        Returns:
            Dict containing extracted symptoms and categories
        """
        # Convert to lowercase for better matching
        text_lower = text.lower()
        
        # Define symptom patterns and categories
        symptom_patterns = {
            "pain": [
                r"\b(headache|head pain|migraine)\b",
                r"\b(stomach pain|abdominal pain|belly ache)\b",
                r"\b(back pain|backache)\b",
                r"\b(chest pain|heart pain)\b",
                r"\b(joint pain|knee pain|hip pain)\b",
                r"\b(toothache|dental pain)\b"
            ],
            "fever": [
                r"\b(fever|high temperature|hot)\b",
                r"\b(chills|shivering)\b"
            ],
            "respiratory": [
                r"\b(cough|coughing)\b",
                r"\b(sore throat|throat pain)\b",
                r"\b(runny nose|stuffy nose|nasal congestion)\b",
                r"\b(shortness of breath|breathing difficulty)\b",
                r"\b(wheezing|chest tightness)\b"
            ],
            "gastrointestinal": [
                r"\b(nausea|nauseous|sick to stomach)\b",
                r"\b(vomiting|throwing up)\b",
                r"\b(diarrhea|loose stools)\b",
                r"\b(constipation|hard stools)\b",
                r"\b(bloating|gas)\b",
                r"\b(heartburn|acid reflux)\b"
            ],
            "fatigue": [
                r"\b(tired|fatigue|exhausted|weak)\b",
                r"\b(dizzy|dizziness|lightheaded)\b"
            ],
            "skin": [
                r"\b(rash|skin rash|hives)\b",
                r"\b(itching|itchy)\b",
                r"\b(swelling|swollen)\b",
                r"\b(redness|red skin)\b"
            ],
            "neurological": [
                r"\b(numbness|tingling)\b",
                r"\b(seizures|convulsions)\b",
                r"\b(memory problems|forgetful)\b",
                r"\b(confusion|disoriented)\b"
            ],
            "general": [
                r"\b(feeling unwell|not feeling well)\b",
                r"\b(loss of appetite)\b",
                r"\b(weight loss|weight gain)\b",
                r"\b(sweating|night sweats)\b"
            ]
        }
        
        extracted_symptoms = {}
        all_symptoms = []
        
        # Extract symptoms by category
        for category, patterns in symptom_patterns.items():
            category_symptoms = []
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    category_symptoms.extend(matches)
            
            if category_symptoms:
                extracted_symptoms[category] = list(set(category_symptoms))
                all_symptoms.extend(category_symptoms)
        
        # Extract duration and severity indicators
        duration_patterns = [
            r"\b(for|since|about|around)\s+(\d+)\s+(days?|weeks?|months?|hours?)\b",
            r"\b(\d+)\s+(days?|weeks?|months?|hours?)\s+(ago|back)\b"
        ]
        
        duration = None
        for pattern in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                duration = match.group(0)
                break
        
        # Extract severity indicators
        severity_indicators = []
        severity_words = ["severe", "bad", "terrible", "awful", "mild", "slight", "moderate"]
        for word in severity_words:
            if word in text_lower:
                severity_indicators.append(word)
        
        return {
            "extracted_symptoms": extracted_symptoms,
            "all_symptoms": list(set(all_symptoms)),
            "duration": duration,
            "severity_indicators": severity_indicators,
            "original_text": text,
            "symptom_count": len(set(all_symptoms))
        }
    
    async def process_speech_to_symptoms(self, audio: UploadFile) -> Dict[str, Any]:
        """
        Complete pipeline: speech to text to symptoms extraction.
        
        Args:
            audio: UploadFile containing audio data
            
        Returns:
            Dict containing transcription and extracted symptoms
        """
        try:
            # Step 1: Convert speech to text
            transcription_result = await self.speech_to_text(audio)
            transcribed_text = transcription_result["transcribed_text"]
            
            # Step 2: Extract symptoms from text
            symptoms_result = self.extract_symptoms(transcribed_text)
            
            # Combine results
            return {
                "transcription": transcription_result,
                "symptoms": symptoms_result,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Speech processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": {"transcribed_text": "", "confidence": 0.0},
                "symptoms": {"extracted_symptoms": {}, "all_symptoms": []}
            } 