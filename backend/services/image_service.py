import cv2
import numpy as np
from fastapi import UploadFile
from typing import Any, Dict, List
from models.symptom_models import ImageAnalysisResult
from datetime import datetime
import io
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ImageAnalysisService:
    """Service for analyzing medical images (skin, rash, etc.) using OpenCV and basic ML"""

    def __init__(self):
        # Define skin condition categories and their characteristics
        self.skin_conditions = {
            "acne": {
                "color_range": [(0, 50, 50), (20, 255, 255)],  # HSV for red/pink
                "texture_keywords": ["bumpy", "inflamed", "red"],
                "severity_levels": ["mild", "moderate", "severe"]
            },
            "eczema": {
                "color_range": [(0, 0, 100), (180, 255, 255)],  # HSV for red patches
                "texture_keywords": ["dry", "scaly", "itchy"],
                "severity_levels": ["mild", "moderate", "severe"]
            },
            "psoriasis": {
                "color_range": [(0, 0, 100), (180, 255, 255)],  # HSV for red
                "texture_keywords": ["thick", "scaly", "silver"],
                "severity_levels": ["mild", "moderate", "severe"]
            },
            "dermatitis": {
                "color_range": [(0, 50, 50), (20, 255, 255)],  # HSV for red
                "texture_keywords": ["red", "swollen", "itchy"],
                "severity_levels": ["mild", "moderate", "severe"]
            },
            "melanoma": {
                "color_range": [(0, 0, 0), (180, 255, 50)],  # HSV for dark
                "texture_keywords": ["asymmetric", "irregular", "dark"],
                "severity_levels": ["suspicious", "high_risk", "critical"]
            }
        }

    async def analyze_medical_image(self, image_file: UploadFile, image_type: str) -> ImageAnalysisResult:
        """Analyze a medical image and return analysis result."""
        try:
            # Read image file
            image_data = await image_file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
            
            # Reset file pointer for potential future use
            image_file.file.seek(0)
            
            # Analyze the image
            analysis = self._analyze_skin_condition(image, image_type)
            
            return ImageAnalysisResult(
                image_type=image_type,
                detected_conditions=analysis["detected_conditions"],
                confidence_scores=analysis["confidence_scores"],
                recommendations=analysis["recommendations"],
                severity_level=analysis["severity_level"],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            # Return a safe fallback result
            return ImageAnalysisResult(
                image_type=image_type,
                detected_conditions=[{"condition": "Analysis failed", "confidence": 0.0}],
                confidence_scores=[0.0],
                recommendations=["Please consult a dermatologist for proper diagnosis"],
                severity_level="unknown",
                timestamp=datetime.now()
            )

    def _analyze_skin_condition(self, image: np.ndarray, image_type: str) -> Dict[str, Any]:
        """Analyze skin condition using computer vision techniques."""
        
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Extract features
        features = self._extract_features(processed_image)
        
        # Analyze based on image type
        if image_type.lower() in ["skin", "rash", "dermatological"]:
            return self._analyze_skin_features(features, processed_image)
        else:
            return self._analyze_general_features(features, processed_image)

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for analysis."""
        # Resize for consistent processing
        height, width = image.shape[:2]
        max_dim = 800
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        return {
            "original": image,
            "hsv": hsv,
            "gray": gray,
            "height": image.shape[0],
            "width": image.shape[1]
        }

    def _extract_features(self, processed_image: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant features from the image."""
        features = {}
        
        # Color analysis
        hsv = processed_image["hsv"]
        gray = processed_image["gray"]
        
        # Calculate color histograms
        features["red_channel"] = cv2.calcHist([processed_image["original"]], [2], None, [256], [0, 256])
        features["green_channel"] = cv2.calcHist([processed_image["original"]], [1], None, [256], [0, 256])
        features["blue_channel"] = cv2.calcHist([processed_image["original"]], [0], None, [256], [0, 256])
        
        # Texture analysis using GLCM-like features
        features["texture"] = self._analyze_texture(gray)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        features["edge_density"] = np.sum(edges > 0) / (processed_image["height"] * processed_image["width"])
        
        # Color segmentation for different skin conditions
        features["color_segments"] = self._segment_colors(hsv)
        
        return features

    def _analyze_texture(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Analyze texture characteristics."""
        # Calculate texture features using simple statistical measures
        texture_features = {}
        
        # Standard deviation (texture roughness)
        texture_features["std_dev"] = np.std(gray_image)
        
        # Variance
        texture_features["variance"] = np.var(gray_image)
        
        # Entropy (texture complexity)
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        texture_features["entropy"] = entropy
        
        return texture_features

    def _segment_colors(self, hsv_image: np.ndarray) -> Dict[str, float]:
        """Segment colors relevant to skin conditions."""
        segments = {}
        
        # Red/pink areas (common in rashes, inflammation)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        segments["red_area"] = np.sum(red_mask > 0) / (hsv_image.shape[0] * hsv_image.shape[1])
        
        # Dark areas (potential melanoma)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 50])
        dark_mask = cv2.inRange(hsv_image, lower_dark, upper_dark)
        segments["dark_area"] = np.sum(dark_mask > 0) / (hsv_image.shape[0] * hsv_image.shape[1])
        
        # Yellow areas (jaundice, certain rashes)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
        segments["yellow_area"] = np.sum(yellow_mask > 0) / (hsv_image.shape[0] * hsv_image.shape[1])
        
        return segments

    def _analyze_skin_features(self, features: Dict[str, Any], processed_image: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze features specific to skin conditions."""
        detected_conditions = []
        confidence_scores = []
        recommendations = []
        
        # Analyze color segments
        color_segments = features["color_segments"]
        
        # Check for red areas (inflammation, rashes)
        if color_segments["red_area"] > 0.1:  # More than 10% red area
            confidence = min(color_segments["red_area"] * 2, 0.9)
            detected_conditions.append({
                "condition": "Skin inflammation",
                "confidence": confidence,
                "area_percentage": color_segments["red_area"] * 100
            })
            confidence_scores.append(confidence)
            
            if confidence > 0.7:
                recommendations.append("High inflammation detected - consider anti-inflammatory treatment")
            else:
                recommendations.append("Mild inflammation - monitor for changes")
        
        # Check for dark areas (potential melanoma)
        if color_segments["dark_area"] > 0.05:  # More than 5% dark area
            confidence = min(color_segments["dark_area"] * 3, 0.95)
            detected_conditions.append({
                "condition": "Dark pigmentation",
                "confidence": confidence,
                "area_percentage": color_segments["dark_area"] * 100
            })
            confidence_scores.append(confidence)
            
            if confidence > 0.6:
                recommendations.append("URGENT: Dark pigmentation detected - consult dermatologist immediately")
            else:
                recommendations.append("Monitor dark areas for changes in size or color")
        
        # Analyze texture for specific conditions
        texture = features["texture"]
        
        # High texture variance might indicate psoriasis or eczema
        if texture["variance"] > 1000:  # High texture variation
            confidence = min(texture["variance"] / 2000, 0.8)
            detected_conditions.append({
                "condition": "Scaly skin condition",
                "confidence": confidence,
                "texture_variance": texture["variance"]
            })
            confidence_scores.append(confidence)
            recommendations.append("Scaly texture detected - may indicate psoriasis or eczema")
        
        # Edge density analysis
        if features["edge_density"] > 0.1:  # High edge density
            confidence = min(features["edge_density"] * 2, 0.7)
            detected_conditions.append({
                "condition": "Irregular skin surface",
                "confidence": confidence,
                "edge_density": features["edge_density"]
            })
            confidence_scores.append(confidence)
            recommendations.append("Irregular surface detected - monitor for changes")
        
        # Determine overall severity
        if detected_conditions:
            max_confidence = max(confidence_scores)
            if max_confidence > 0.8:
                severity = "high"
            elif max_confidence > 0.5:
                severity = "medium"
            else:
                severity = "low"
        else:
            severity = "low"
            detected_conditions.append({
                "condition": "Normal skin appearance",
                "confidence": 0.8
            })
            confidence_scores.append(0.8)
            recommendations.append("No concerning features detected - continue regular monitoring")
        
        return {
            "detected_conditions": detected_conditions,
            "confidence_scores": confidence_scores,
            "recommendations": recommendations,
            "severity_level": severity
        }

    def _analyze_general_features(self, features: Dict[str, Any], processed_image: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze general image features for non-skin specific analysis."""
        # Fallback analysis for other image types
        return {
            "detected_conditions": [{"condition": "General image analysis", "confidence": 0.5}],
            "confidence_scores": [0.5],
            "recommendations": ["Please consult a medical professional for proper diagnosis"],
            "severity_level": "unknown"
        } 