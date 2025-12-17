"""
Vision Service for Google Cloud Vision API
Classifies trash images as PLASTIC or NON_PLASTIC
"""
from google.cloud import vision
import base64
import logging
from typing import Dict, Optional
from config import get_google_credentials_path
import os

logger = logging.getLogger(__name__)

# Accepted labels - STRICT: Only explicit plastic bottles and metal cans
ACCEPTED_LABELS = [
    # Explicit plastic bottles only
    'plastic bottle', 'water bottle', 'soda bottle', 'drink bottle',
    'bottled water', 'drinking water',
    
    # Explicit metal cans only
    'aluminum can', 'tin can', 'soda can', 'beer can', 'drink can',
    'steel and tin cans', 'soft drink can',
]

# Rejected labels (common non-acceptable items - INCLUDING GLASS and FLASHLIGHTS)
REJECTED_LABELS = [
    # Glass items (explicit rejection)
    'glass', 'glass bottle', 'wine bottle', 'beer bottle', 'glass container',
    'jar', 'glass jar', 'ceramic', 'porcelain',
    
    # Generic terms that cause false positives
    'container', 'drinkware', 'beverage', 'drink',  # Reject generic containers
    'bottle',  # Reject generic "bottle" without "plastic"
    'can',     # Reject generic "can" without "aluminum/tin"
    
    # Electronic devices (flashlights, etc.)
    'flashlight', 'torch', 'light', 'lamp', 'electronic device', 'device',
    'battery', 'metal scrap',
    
    # Other non-acceptable items
    'bin', 'trash can', 'garbage can', 'wastebasket',
    'bag', 'plastic bag', 'paper bag',
    'box', 'cardboard box',
    'cup', 'mug', 'coffee cup',
    'food', 'fruit', 'vegetable',
    'book', 'paper', 'newspaper'
]


class VisionService:
    """Service for Google Cloud Vision API integration"""
    
    def __init__(self):
        """Initialize Vision API client"""
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Google Cloud Vision client"""
        try:
            creds_path = get_google_credentials_path()
            if creds_path and os.path.exists(creds_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                self.client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision client initialized successfully")
            else:
                logger.warning("Google Cloud credentials not found. Vision API will not work.")
                self.client = None
        except Exception as e:
            logger.error(f"Error initializing Vision client: {str(e)}")
            self.client = None
    
    async def classify_trash(self, image_base64: str) -> Dict[str, any]:
        """
        Classify trash image using Google Cloud Vision API
        
        Args:
            image_base64: Base64 encoded JPEG image
            
        Returns:
            Dict with material_type, confidence, and labels
        """
        if not self.client:
            raise Exception("Google Cloud Vision API not configured. Please set GOOGLE_APPLICATION_CREDENTIALS.")
        
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = vision.Image(content=image_data)
            
            # Perform label detection
            response = self.client.label_detection(image=image)
            labels = response.label_annotations
            
            # Process labels to determine material type
            result = self._process_labels(labels)
            
            return {
                "material_type": result["type"],
                "confidence": result["confidence"],
                "labels": [{"name": l.description, "score": l.score} for l in labels[:5]]
            }
        except Exception as e:
            logger.error(f"Vision API error: {str(e)}")
            raise
    
    def _process_labels(self, labels) -> Dict[str, any]:
        """
        Process Vision API labels to determine PLASTIC vs NON_PLASTIC
        Uses strict validation logic from test_computer_vision.py
        """
        accepted_items = []
        rejected_items = []
        
        for label in labels:
            label_name = label.description.lower()
            label_words = set(label_name.split())
            confidence = label.score
            
            # Check if accepted (STRICT: must be in ACCEPTED_LABELS explicitly)
            is_accepted = False
            for accepted in ACCEPTED_LABELS:
                accepted_words = set(accepted.split())
                if accepted_words.issubset(label_words) or accepted in label_name:
                    is_accepted = True
                    break
            
            # Additional validation: even if in ACCEPTED_LABELS, double-check
            if is_accepted:
                has_plastic = 'plastic' in label_words
                has_aluminum = 'aluminum' in label_words or 'tin' in label_words or 'steel' in label_words
                has_bottle = 'bottle' in label_words
                has_can = 'can' in label_words
                
                # For bottles: must have "plastic" or be specific (water bottle, soda bottle)
                if has_bottle and not has_plastic and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words:
                    is_accepted = False
                
                # For cans: must have "aluminum", "tin", "steel" or be specific (soda can, beer can)
                if has_can and not has_aluminum and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words:
                    is_accepted = False
            
            # Only check REJECTED_LABELS if not already accepted
            is_rejected = False
            if not is_accepted:
                rejected_words = set()
                for rejected in REJECTED_LABELS:
                    rejected_words.update(rejected.split())
                
                is_rejected = any(rejected_word in label_words for rejected_word in rejected_words)
                
                # Explicit rejection checks
                if 'glass' in label_words or 'jar' in label_words:
                    is_rejected = True
                
                # Reject generic "bottle" without "plastic"
                if label_name == 'bottle' or (label_name.startswith('bottle ') and 'plastic' not in label_words and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words):
                    is_rejected = True
                
                # Reject generic "can" without material keywords
                if label_name == 'can' or (label_name.endswith(' can') and 'aluminum' not in label_words and 'tin' not in label_words and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words and 'steel' not in label_words):
                    is_rejected = True
                
                # Reject generic containers
                if label_name in ['container', 'drinkware', 'beverage', 'drink']:
                    is_rejected = True
            
            # Final check: reject glass even if it was accepted
            if 'glass' in label_words or 'jar' in label_words:
                is_rejected = True
                is_accepted = False
            
            if is_rejected:
                rejected_items.append({
                    'name': label.description,
                    'confidence': confidence
                })
            elif is_accepted:
                # Final check: make absolutely sure it's not glass or generic
                if 'glass' not in label_words and 'jar' not in label_words and label_name not in ['container', 'drinkware', 'beverage', 'drink', 'bottle', 'can']:
                    accepted_items.append({
                        'name': label.description,
                        'confidence': confidence
                    })
        
        # Determine result
        if accepted_items:
            # Get highest confidence accepted item
            best_item = max(accepted_items, key=lambda x: x['confidence'])
            
            # Determine material type (PLASTIC for bottles, NON_PLASTIC for cans)
            item_name_lower = best_item['name'].lower()
            if "bottle" in item_name_lower and "glass" not in item_name_lower:
                material_type = "PLASTIC"
            elif "can" in item_name_lower:
                material_type = "NON_PLASTIC"
            else:
                material_type = "PLASTIC"  # Default to plastic for bottles
            
            return {
                "type": material_type,
                "confidence": best_item['confidence']
            }
        else:
            # No acceptable items detected - reject
            return {
                "type": "NON_PLASTIC",  # Default to non-plastic if uncertain
                "confidence": 0.5
            }


# Global instance
vision_service = VisionService()


