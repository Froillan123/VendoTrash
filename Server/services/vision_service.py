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
            
            # Log ALL Cloud Vision API labels for debugging
            logger.info("=" * 60)
            logger.info("🔍 CLOUD VISION API DETECTION RESULTS:")
            logger.info("=" * 60)
            logger.info(f"Total labels detected: {len(labels)}")
            logger.info("")
            logger.info("All detected labels:")
            for i, label in enumerate(labels[:10], 1):  # Show top 10 labels
                logger.info(f"  {i}. {label.description:30s} (Confidence: {label.score*100:.1f}%)")
            logger.info("")
            
            # Process labels to determine material type
            result = self._process_labels(labels)
            
            logger.info(f"✅ Final Classification: {result['type']} (Confidence: {result['confidence']*100:.1f}%)")
            logger.info("=" * 60)
            
            # Map "type" from _process_labels to "material_type" for response
            material_type = result["type"]
            
            return {
                "material_type": material_type,
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
        IMPROVED: Considers label combinations (e.g., "Plastic" + "Drinking water" = plastic bottle)
        """
        accepted_items = []
        rejected_items = []
        unknown_items = []
        
        # First pass: collect all label info for context-aware processing
        all_labels_info = []
        for label in labels:
            label_name = label.description.lower()
            label_words = set(label_name.split())
            all_labels_info.append({
                'name': label.description,
                'name_lower': label_name,
                'words': label_words,
                'confidence': label.score
            })
        
        # Check for context clues (bottle/can related labels)
        has_bottle_context = any('bottle' in info['words'] or 'water' in info['words'] or 'soda' in info['words'] or 'drink' in info['words'] for info in all_labels_info)
        has_can_context = any('can' in info['words'] or 'aluminum' in info['words'] or 'tin' in info['words'] or 'steel' in info['words'] for info in all_labels_info)
        has_plastic_context = any('plastic' in info['words'] for info in all_labels_info)
        has_glass_context = any('glass' in info['words'] or 'jar' in info['words'] for info in all_labels_info)
        has_transparency = any('transparency' in info['words'] or 'transparent' in info['words'] for info in all_labels_info)
        has_silver_metallic = any('silver' in info['words'] or 'metallic' in info['words'] for info in all_labels_info)
        
        logger.info("Processing labels for classification...")
        
        for label_info in all_labels_info:
            label_name = label_info['name_lower']
            label_words = label_info['words']
            confidence = label_info['confidence']
            label_description = label_info['name']
            
            # Check if accepted (STRICT: must be in ACCEPTED_LABELS explicitly)
            is_accepted = False
            is_explicitly_accepted = False  # Track if label is explicitly in ACCEPTED_LABELS
            for accepted in ACCEPTED_LABELS:
                accepted_words = set(accepted.split())
                if accepted_words.issubset(label_words) or accepted in label_name:
                    is_accepted = True
                    # Check if it's an exact or near-exact match (explicitly accepted)
                    if accepted == label_name or accepted in label_name or label_name in accepted:
                        is_explicitly_accepted = True
                    break
            
            # Additional validation: even if in ACCEPTED_LABELS, double-check
            # BUT: Don't reject if it's explicitly in ACCEPTED_LABELS (like "drinking water", "plastic bottle")
            if is_accepted:
                has_plastic = 'plastic' in label_words
                has_aluminum = 'aluminum' in label_words or 'tin' in label_words or 'steel' in label_words
                has_bottle = 'bottle' in label_words
                has_can = 'can' in label_words
                
                # Only apply strict validation if NOT explicitly in ACCEPTED_LABELS
                if not is_explicitly_accepted:
                    # For bottles: must have "plastic" or be specific (water bottle, soda bottle)
                    if has_bottle and not has_plastic and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words:
                        is_accepted = False
                    
                    # For cans: must have "aluminum", "tin", "steel" or be specific (soda can, beer can)
                    if has_can and not has_aluminum and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words:
                        is_accepted = False
            
            # CONTEXT-AWARE: If "Plastic" appears with bottle-related context, accept it
            if not is_accepted and label_name == 'plastic' and has_bottle_context and not has_glass_context:
                # "Plastic" + "Drinking water" or "Bottled water" = plastic bottle
                if any('water' in info['words'] or 'bottle' in info['words'] for info in all_labels_info if info != label_info):
                    is_accepted = True
                    # Create a combined label for better logging
                    label_description = f"Plastic bottle (from: Plastic + context)"
            
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
                
                # Reject generic "bottle" without "plastic" (unless context suggests otherwise)
                if label_name == 'bottle' or (label_name.startswith('bottle ') and 'plastic' not in label_words and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words):
                    # But don't reject if there's plastic context
                    if not has_plastic_context:
                        is_rejected = True
                
                # Reject generic "can" without material keywords
                if label_name == 'can' or (label_name.endswith(' can') and 'aluminum' not in label_words and 'tin' not in label_words and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words and 'steel' not in label_words):
                    is_rejected = True
                
                # Reject generic "Plastic" alone (without bottle/can context)
                if label_name == 'plastic' and not has_bottle_context and not has_can_context:
                    is_rejected = True
                
                # Reject generic containers
                if label_name in ['container', 'drinkware', 'beverage', 'drink']:
                    is_rejected = True
            
            # Final check: reject glass even if it was accepted
            # BUT: Only reject if THIS SPECIFIC LABEL has glass, not if other labels have glass
            # If we have transparency + bottle context, it might be a clear plastic bottle
            # (clear plastic bottles can be misidentified as "glass" by Vision API)
            # IMPORTANT: Don't reject if this label is explicitly in ACCEPTED_LABELS
            if ('glass' in label_words or 'jar' in label_words) and not is_explicitly_accepted:
                # Only reject if we don't have transparency + bottle context (clear plastic bottle case)
                if not (has_transparency and has_bottle_context):
                    is_rejected = True
                    is_accepted = False
            
            if is_rejected:
                rejected_items.append({
                    'name': label_description,
                    'confidence': confidence
                })
                logger.info(f"  ❌ REJECTED: {label_description} ({confidence*100:.1f}%)")
            elif is_accepted:
                # Final check: make absolutely sure THIS LABEL is not glass or generic
                # Only check THIS label's words, not global has_glass_context
                if 'glass' not in label_words and 'jar' not in label_words:
                    # For generic bottle/can, only reject if no plastic/aluminum context
                    if label_name in ['bottle', 'can']:
                        # If it's a generic "bottle" or "can", check if we have material context
                        if (label_name == 'bottle' and has_plastic_context) or (label_name == 'can' and has_can_context):
                            accepted_items.append({
                                'name': label_description,
                                'confidence': confidence
                            })
                            logger.info(f"  ✅ ACCEPTED: {label_description} ({confidence*100:.1f}%)")
                        else:
                            rejected_items.append({
                                'name': label_description,
                                'confidence': confidence
                            })
                            logger.info(f"  ❌ REJECTED (Generic): {label_description} ({confidence*100:.1f}%)")
                    elif label_name not in ['container', 'drinkware', 'beverage', 'drink']:
                        accepted_items.append({
                            'name': label_description,
                            'confidence': confidence
                        })
                        logger.info(f"  ✅ ACCEPTED: {label_description} ({confidence*100:.1f}%)")
                    else:
                        rejected_items.append({
                            'name': label_description,
                            'confidence': confidence
                        })
                        logger.info(f"  ❌ REJECTED (Generic): {label_description} ({confidence*100:.1f}%)")
                else:
                    rejected_items.append({
                        'name': label_description,
                        'confidence': confidence
                    })
                    logger.info(f"  ❌ REJECTED (Glass/Jar): {label_description} ({confidence*100:.1f}%)")
            else:
                unknown_items.append({
                    'name': label_description,
                    'confidence': confidence
                })
                logger.info(f"  ⚠️  UNKNOWN: {label_description} ({confidence*100:.1f}%)")
        
        # Log summary
        logger.info("")
        logger.info("Classification Summary:")
        logger.info(f"  ✅ Accepted items: {len(accepted_items)}")
        logger.info(f"  ❌ Rejected items: {len(rejected_items)}")
        logger.info(f"  ⚠️  Unknown items: {len(unknown_items)}")
        logger.info("")
        
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
            
            logger.info(f"🎯 Best match: {best_item['name']} → {material_type}")
            
            return {
                "type": material_type,
                "confidence": best_item['confidence']
            }
        else:
            # FALLBACK: If no explicit accepted items, check for context clues
            # This handles cases where Vision API detects generic labels like "Glass", "Transparency", "Silver"
            # but the item might still be a plastic bottle (clear bottles can be detected as "glass")
            
            # If we have transparency + bottle context (even if "glass" was detected), might be clear plastic bottle
            # Clear plastic bottles often get misidentified as "glass" by Vision API
            if has_transparency and has_bottle_context:
                logger.info("🔍 FALLBACK: Transparency + bottle context detected - likely clear plastic bottle")
                # Use highest confidence label as base
                best_label = max(all_labels_info, key=lambda x: x['confidence'])
                return {
                    "type": "PLASTIC",
                    "confidence": best_label['confidence'] * 0.7  # Lower confidence for fallback
                }
            
            # If "Glass" + "Transparency" detected together, likely a clear plastic bottle (not actual glass)
            if has_glass_context and has_transparency:
                logger.info("🔍 FALLBACK: Glass + Transparency detected - likely clear plastic bottle (not actual glass)")
                best_label = max(all_labels_info, key=lambda x: x['confidence'])
                return {
                    "type": "PLASTIC",
                    "confidence": best_label['confidence'] * 0.65  # Lower confidence for fallback
                }
            
            # If we have silver/metallic + can context, might be metal can
            if has_silver_metallic and has_can_context and not has_glass_context:
                logger.info("🔍 FALLBACK: Metallic + can context detected - likely metal can")
                best_label = max(all_labels_info, key=lambda x: x['confidence'])
                return {
                    "type": "NON_PLASTIC",
                    "confidence": best_label['confidence'] * 0.7  # Lower confidence for fallback
                }
            
            # No acceptable items detected - REJECT
            logger.info("🚫 No acceptable items found. Item REJECTED.")
            return {
                "type": "REJECTED",
                "confidence": 0.0
            }


# Global instance
vision_service = VisionService()


