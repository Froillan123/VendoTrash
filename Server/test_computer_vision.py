"""
Computer Vision Test Script for VendoTrash
Detects plastic bottles and cans, rejects other objects
GUI application for testing
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import io
import json
import logging
from typing import Optional, List, Dict
from google.cloud import vision
from config import get_google_credentials_path

# Try to import cv2, but make it optional
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available. Webcam feature will be disabled.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Accepted labels - STRICT: Only explicit plastic bottles and metal cans
# Must have material keyword (plastic/aluminum/tin) + type (bottle/can)
ACCEPTED_LABELS = [
    # Explicit plastic bottles only
    'plastic bottle', 'water bottle', 'soda bottle', 'drink bottle',
    'bottled water', 'drinking water',
    
    # Explicit metal cans only
    'aluminum can', 'tin can', 'soda can', 'beer can', 'drink can',
    'steel and tin cans', 'soft drink can',
    
    # REMOVED generic terms that cause false positives:
    # 'bottle' - too generic (could be glass)
    # 'can' - too generic (could be anything)
    # 'container' - too generic (flashlights, boxes, everything)
    # 'drinkware' - too generic (cups, mugs, flashlights)
    # 'beverage' - too generic
    # 'drink' - too generic
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


class ComputerVisionTester:
    def __init__(self, root):
        self.root = root
        self.root.title("VendoTrash - Computer Vision Tester")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize Google Cloud Vision client
        self.vision_client = None
        self.init_vision_client()
        
        # Current image
        self.current_image = None
        self.current_image_path = None
        self.cap = None  # Webcam capture
        self.last_detection_time = 0
        self.detection_interval = 1.0  # Detect every 1 second in real-time mode
        self.is_detecting = False  # Prevent overlapping detections
        
        # Setup GUI
        self.setup_gui()
        
    def init_vision_client(self):
        """Initialize Google Cloud Vision API client"""
        try:
            creds_path = get_google_credentials_path()
            if creds_path and os.path.exists(creds_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
                self.vision_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision client initialized successfully")
            else:
                logger.warning("Google Cloud credentials not found. Vision API will not work.")
                messagebox.showwarning(
                    "Warning",
                    "Google Cloud Vision credentials not found.\n"
                    "Please set GOOGLE_APPLICATION_CREDENTIALS in .env file.\n"
                    "Detection will use basic image analysis."
                )
        except Exception as e:
            logger.error(f"Error initializing Vision client: {str(e)}")
            # Don't show error dialog - allow fallback mode
            self.vision_client = None
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2d8659', height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🔍 VendoTrash Computer Vision Tester",
            font=('Arial', 18, 'bold'),
            bg='#2d8659',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Image display
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Image label
        self.image_label = tk.Label(
            left_frame,
            text="No image loaded\n\nClick 'Load Image' or 'Use Webcam'",
            bg='white',
            fg='gray',
            font=('Arial', 12),
            width=50,
            height=20
        )
        self.image_label.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        # Right panel - Controls and results
        right_frame = tk.Frame(main_frame, bg='#f0f0f0', width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Control buttons
        control_frame = tk.LabelFrame(right_frame, text="Controls", bg='#f0f0f0', font=('Arial', 10, 'bold'))
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_load = tk.Button(
            control_frame,
            text="📁 Load Image",
            command=self.load_image,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        btn_load.pack(fill=tk.X, padx=10, pady=5)
        
        btn_webcam = tk.Button(
            control_frame,
            text="📷 Use Webcam" + (" (Not Available)" if not CV2_AVAILABLE else ""),
            command=self.toggle_webcam,
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED if not CV2_AVAILABLE else tk.NORMAL
        )
        btn_webcam.pack(fill=tk.X, padx=10, pady=5)
        self.btn_webcam = btn_webcam
        
        btn_detect = tk.Button(
            control_frame,
            text="🔍 Detect Objects",
            command=self.detect_objects,
            bg='#FF9800',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=10,
            cursor='hand2',
            state=tk.DISABLED
        )
        btn_detect.pack(fill=tk.X, padx=10, pady=5)
        self.btn_detect = btn_detect
        
        # Real-time detection toggle
        self.realtime_detection = tk.BooleanVar()
        btn_realtime = tk.Checkbutton(
            control_frame,
            text="🔄 Real-time Detection",
            variable=self.realtime_detection,
            command=self.toggle_realtime,
            bg='#f0f0f0',
            font=('Arial', 10),
            activebackground='#f0f0f0',
            cursor='hand2'
        )
        btn_realtime.pack(fill=tk.X, padx=10, pady=5)
        self.realtime_active = False
        
        # Results frame
        results_frame = tk.LabelFrame(right_frame, text="Detection Results", bg='#f0f0f0', font=('Arial', 10, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            results_frame,
            text="Ready",
            bg='#f0f0f0',
            fg='gray',
            font=('Arial', 11),
            wraplength=280
        )
        self.status_label.pack(padx=10, pady=10)
        
        # Results text
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            width=30,
            height=15,
            font=('Courier', 9),
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar for results
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Status indicator
        self.status_indicator = tk.Label(
            results_frame,
            text="⚪ Waiting",
            bg='#f0f0f0',
            font=('Arial', 12, 'bold'),
            pady=10
        )
        self.status_indicator.pack(pady=5)
        
    def load_image(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.btn_detect.config(state=tk.NORMAL)
            self.update_status("Image loaded", "ready")
    
    def toggle_webcam(self):
        """Toggle webcam capture"""
        if not CV2_AVAILABLE:
            messagebox.showwarning(
                "Webcam Not Available",
                "OpenCV is not installed or not compatible.\n"
                "Please install: pip install opencv-python numpy<2.0.0\n\n"
                "You can still use 'Load Image' to test with image files."
            )
            return
        
        if self.cap is None:
            # Start webcam
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open webcam")
                self.cap = None
                return
            
            self.update_status("Webcam active", "ready")
            self.btn_detect.config(state=tk.NORMAL)
            self.btn_webcam.config(text="📷 Stop Webcam")
            self.capture_webcam_frame()
        else:
            # Stop webcam
            self.realtime_active = False
            self.realtime_detection.set(False)
            self.cap.release()
            self.cap = None
            self.update_status("Webcam stopped", "ready")
            self.btn_webcam.config(text="📷 Use Webcam" + (" (Not Available)" if not CV2_AVAILABLE else ""))
            self.image_label.config(image='', text="No image loaded\n\nClick 'Load Image' or 'Use Webcam'")
    
    def capture_webcam_frame(self):
        """Capture frame from webcam"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_image = frame_rgb
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize for display
                display_image = self.resize_for_display(pil_image)
                photo = ImageTk.PhotoImage(display_image)
                
                self.image_label.config(image=photo, text='')
                self.image_label.image = photo
                
                # Real-time detection if enabled
                if self.realtime_active:
                    self.detect_objects_silent()
                
                # Continue capturing
                self.root.after(30, self.capture_webcam_frame)
    
    def display_image(self, image_path: str):
        """Display image in the GUI"""
        try:
            image = Image.open(image_path)
            
            # Convert to RGB array for detection (using PIL instead of cv2 if needed)
            if CV2_AVAILABLE:
                self.current_image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
            else:
                # Use PIL to convert to RGB array
                self.current_image = image.convert('RGB')
            
            # Resize for display
            display_image = self.resize_for_display(image)
            photo = ImageTk.PhotoImage(display_image)
            
            self.image_label.config(image=photo, text='')
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def resize_for_display(self, image: Image.Image, max_size=(600, 500)) -> Image.Image:
        """Resize image for display while maintaining aspect ratio"""
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def detect_objects(self):
        """Detect objects in the current image"""
        if self.current_image is None and self.current_image_path is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        self.update_status("Detecting objects...", "processing")
        self.results_text.delete(1.0, tk.END)
        
        try:
            # Prepare image for Vision API
            if self.current_image_path:
                # Use file path
                with open(self.current_image_path, 'rb') as image_file:
                    content = image_file.read()
            else:
                # Use current image from webcam or loaded image
                if isinstance(self.current_image, Image.Image):
                    pil_image = self.current_image
                else:
                    # It's a numpy array from cv2
                    pil_image = Image.fromarray(self.current_image)
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='JPEG')
                content = img_byte_arr.getvalue()
            
            # Detect using Google Cloud Vision
            if self.vision_client:
                image = vision.Image(content=content)
                response = self.vision_client.label_detection(image=image)
                labels = response.label_annotations
                
                self.process_detection_results(labels)
            else:
                # Fallback: Basic analysis
                self.fallback_detection()
                
        except Exception as e:
            error_str = str(e)
            logger.error(f"Detection error: {error_str}")
            
            # Check if it's an API not enabled error
            if "SERVICE_DISABLED" in error_str or "403" in error_str or "has not been used" in error_str.lower():
                # Extract activation URL if present
                activation_url = "https://console.developers.google.com/apis/api/vision.googleapis.com/overview"
                if "activationUrl" in error_str or "console.developers.google.com" in error_str:
                    # Try to extract URL from error message
                    import re
                    url_match = re.search(r'https://console\.developers\.google\.com[^\s\)]+', error_str)
                    if url_match:
                        activation_url = url_match.group(0)
                
                error_msg = (
                    "Cloud Vision API is not enabled for your project.\n\n"
                    f"Please enable it by visiting:\n{activation_url}\n\n"
                    "After enabling, wait a few minutes for it to propagate,\n"
                    "then try again."
                )
                messagebox.showerror("Vision API Not Enabled", error_msg)
                self.update_status("Vision API not enabled - check console", "error")
            else:
                messagebox.showerror("Error", f"Detection failed: {error_str}")
                self.update_status("Detection failed", "error")
    
    def process_detection_results(self, labels: List):
        """Process Google Cloud Vision detection results"""
        detected_items = []
        accepted_items = []
        rejected_items = []
        
        self.results_text.insert(tk.END, "=== DETECTION RESULTS ===\n\n")
        self.results_text.insert(tk.END, f"Found {len(labels)} labels:\n\n")
        
        for label in labels:
            label_name = label.description.lower()
            confidence = label.score * 100
            
            detected_items.append({
                'name': label.description,
                'confidence': confidence
            })
            
            # STRICT VALIDATION: Check ACCEPTED_LABELS FIRST, then REJECTED_LABELS
            # Use word-level matching to avoid false positives (e.g., "aluminum can" shouldn't match "can")
            label_words = set(label_name.split())
            
            # Check if accepted (STRICT: must be in ACCEPTED_LABELS explicitly)
            # Use word-level matching for better accuracy
            is_accepted = False
            for accepted in ACCEPTED_LABELS:
                accepted_words = set(accepted.split())
                # Check if all words from accepted label are present in the detected label
                # OR if the accepted phrase is contained in the label
                if accepted_words.issubset(label_words) or accepted in label_name:
                    is_accepted = True
                    break
            
            # Additional validation: even if in ACCEPTED_LABELS, double-check
            if is_accepted:
                # Must have explicit material keyword (check words, not substring)
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
                
                # Check if any rejected word appears as a standalone word (not as part of another word)
                is_rejected = any(rejected_word in label_words for rejected_word in rejected_words)
                
                # Explicit rejection checks (glass, jars, flashlights, generic terms)
                if 'glass' in label_words or 'jar' in label_words:
                    is_rejected = True
                
                # Reject generic "bottle" (exact match or standalone word)
                if label_name == 'bottle' or (label_name.startswith('bottle ') and 'plastic' not in label_words and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words):
                    is_rejected = True
                
                # Reject generic "can" (exact match or standalone word without material keywords)
                if label_name == 'can' or (label_name.endswith(' can') and 'aluminum' not in label_words and 'tin' not in label_words and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words and 'steel' not in label_words):
                    is_rejected = True
                
                # Reject generic containers (flashlights, boxes, etc.) - exact match only
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
                self.results_text.insert(tk.END, f"❌ REJECTED: {label.description}\n")
                self.results_text.insert(tk.END, f"   Confidence: {confidence:.1f}%\n\n")
            elif is_accepted:
                # Final check: make absolutely sure it's not glass or generic (use word-level check)
                if 'glass' not in label_words and 'jar' not in label_words and label_name not in ['container', 'drinkware', 'beverage', 'drink', 'bottle', 'can']:
                    accepted_items.append({
                        'name': label.description,
                        'confidence': confidence
                    })
                    self.results_text.insert(tk.END, f"✅ ACCEPTED: {label.description}\n")
                    self.results_text.insert(tk.END, f"   Confidence: {confidence:.1f}%\n\n")
                else:
                    # Failed final check - reject it
                    rejected_items.append({
                        'name': label.description,
                        'confidence': confidence
                    })
                    self.results_text.insert(tk.END, f"❌ REJECTED: {label.description} (Generic/Glass)\n")
                    self.results_text.insert(tk.END, f"   Confidence: {confidence:.1f}%\n\n")
            else:
                # Unknown item - reject by default (STRICT mode)
                self.results_text.insert(tk.END, f"⚠️  UNKNOWN: {label.description}\n")
                self.results_text.insert(tk.END, f"   Confidence: {confidence:.1f}% (REJECTED)\n\n")
        
        # Summary
        self.results_text.insert(tk.END, "\n=== SUMMARY ===\n")
        self.results_text.insert(tk.END, f"Total labels: {len(detected_items)}\n")
        self.results_text.insert(tk.END, f"✅ Accepted: {len(accepted_items)}\n")
        self.results_text.insert(tk.END, f"❌ Rejected: {len(rejected_items) + (len(detected_items) - len(accepted_items) - len(rejected_items))}\n")
        
        # Final decision
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
            
            self.results_text.insert(tk.END, f"\n🎯 RESULT: ACCEPTED\n")
            self.results_text.insert(tk.END, f"Material: {material_type}\n")
            self.results_text.insert(tk.END, f"Item: {best_item['name']}\n")
            self.results_text.insert(tk.END, f"Confidence: {best_item['confidence']:.1f}%\n")
            
            self.update_status(f"✅ ACCEPTED: {best_item['name']} ({material_type})", "accepted")
        else:
            self.results_text.insert(tk.END, f"\n🚫 RESULT: REJECTED\n")
            self.results_text.insert(tk.END, "No acceptable items detected\n")
            self.results_text.insert(tk.END, "Only PLASTIC bottles and METAL cans are accepted\n")
            self.results_text.insert(tk.END, "Glass bottles, jars, flashlights, and generic containers are REJECTED\n")
            self.results_text.insert(tk.END, "Must have explicit material keyword (plastic/aluminum/tin)\n")
            
            self.update_status("❌ REJECTED: Not a plastic bottle or metal can", "rejected")
        
        self.results_text.see(tk.END)
    
    def toggle_realtime(self):
        """Toggle real-time detection"""
        if self.cap is None or not self.cap.isOpened():
            self.realtime_detection.set(False)
            messagebox.showwarning("Warning", "Please start webcam first")
            return
        
        self.realtime_active = self.realtime_detection.get()
        if self.realtime_active:
            self.update_status("Real-time detection active", "processing")
        else:
            self.update_status("Real-time detection stopped", "ready")
    
    def detect_objects_silent(self):
        """Detect objects without updating GUI (for real-time) - throttled"""
        import time
        
        if self.current_image is None or self.is_detecting:
            return
        
        # Throttle detection to avoid too many API calls (every 1 second)
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return
        
        self.is_detecting = True
        self.last_detection_time = current_time
        
        try:
            # Prepare image for Vision API (lower quality for faster processing)
            pil_image = Image.fromarray(self.current_image)
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            content = img_byte_arr.getvalue()
            
            # Detect using Google Cloud Vision
            if self.vision_client:
                image = vision.Image(content=content)
                response = self.vision_client.label_detection(image=image, max_results=10)
                labels = response.label_annotations
                
                # Quick check for accepted items
                accepted = False
                material_type = None
                best_item = None
                best_confidence = 0
                
                for label in labels:
                    label_name = label.description.lower()
                    label_words = set(label_name.split())
                    
                    # STRICT: Check ACCEPTED_LABELS FIRST, then REJECTED_LABELS
                    # Check if accepted (STRICT: must be in ACCEPTED_LABELS and have material keyword)
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
                        
                        # For bottles: must have "plastic" or be specific
                        if has_bottle and not has_plastic and 'water' not in label_words and 'soda' not in label_words and 'drink' not in label_words:
                            is_accepted = False
                        
                        # For cans: must have "aluminum/tin/steel" or be specific (soda/beer can)
                        if has_can and not has_aluminum and 'soda' not in label_words and 'beer' not in label_words and 'drink' not in label_words:
                            is_accepted = False
                    
                    # Only check REJECTED_LABELS if not already accepted
                    is_rejected = False
                    if not is_accepted:
                        rejected_words = set()
                        for rejected in REJECTED_LABELS:
                            rejected_words.update(rejected.split())
                        
                        is_rejected = any(rejected_word in label_words for rejected_word in rejected_words)
                        if 'glass' in label_words or 'jar' in label_words:
                            is_rejected = True
                        
                        # Reject generic "bottle" without "plastic"
                        if label_name == 'bottle' or (label_name.startswith('bottle ') and 'plastic' not in label_words and 'water' not in label_words and 'soda' not in label_words):
                            is_rejected = True
                        
                        # Reject generic "can" without material keyword
                        if label_name == 'can' or (label_name.endswith(' can') and 'aluminum' not in label_words and 'tin' not in label_words and 'steel' not in label_words and 'soda' not in label_words and 'beer' not in label_words):
                            is_rejected = True
                        
                        # Reject generic containers
                        if label_name in ['container', 'drinkware', 'beverage', 'drink']:
                            is_rejected = True
                    
                    # Final check: reject glass even if it was accepted
                    if 'glass' in label_words or 'jar' in label_words:
                        is_rejected = True
                        is_accepted = False
                    
                    if is_accepted and not is_rejected and label.score > best_confidence:
                        accepted = True
                        if "bottle" in label_words:
                            material_type = "PLASTIC"
                        else:
                            material_type = "NON_PLASTIC"
                        best_item = label.description
                        best_confidence = label.score
                
                # Update status only
                if accepted:
                    confidence_pct = best_confidence * 100
                    self.update_status(f"✅ ACCEPTED: {best_item} ({material_type}) - {confidence_pct:.0f}%", "accepted")
                else:
                    self.update_status("❌ REJECTED: Not a plastic bottle or metal can", "rejected")
            else:
                self.update_status("⚠️ Vision API not available", "error")
                    
        except Exception as e:
            error_str = str(e)
            # Check if it's an API not enabled error
            if "SERVICE_DISABLED" in error_str or "403" in error_str or "has not been used" in error_str.lower():
                self.update_status("⚠️ Vision API not enabled - enable in Google Cloud Console", "error")
                # Stop real-time detection if API is not enabled
                self.realtime_active = False
                self.realtime_detection.set(False)
            else:
                # Silent fail for other errors (don't spam errors)
                logger.debug(f"Real-time detection error: {error_str}")
        finally:
            self.is_detecting = False
    
    def fallback_detection(self):
        """Fallback detection when Vision API is not available"""
        self.results_text.insert(tk.END, "⚠️  Google Cloud Vision API not available\n\n")
        self.results_text.insert(tk.END, "Using basic image analysis...\n\n")
        self.results_text.insert(tk.END, "Please configure GOOGLE_APPLICATION_CREDENTIALS\n")
        self.results_text.insert(tk.END, "in your .env file to enable full detection.\n")
        
        self.update_status("Vision API not configured", "error")
    
    def update_status(self, message: str, status: str):
        """Update status label and indicator"""
        self.status_label.config(text=message)
        
        if status == "ready":
            self.status_indicator.config(text="⚪ Ready", fg='gray')
        elif status == "processing":
            self.status_indicator.config(text="🔄 Processing...", fg='orange')
        elif status == "accepted":
            self.status_indicator.config(text="✅ ACCEPTED", fg='green')
        elif status == "rejected":
            self.status_indicator.config(text="❌ REJECTED", fg='red')
        elif status == "error":
            self.status_indicator.config(text="⚠️  Error", fg='red')


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = ComputerVisionTester(root)
    
    # Handle window close
    def on_closing():
        if app.cap:
            app.cap.release()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

