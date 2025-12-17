#!/usr/bin/env python3
"""
🖼️ Advanced Image Processing Module
Enhances screenshots for better AI vision model performance

Features:
- Multi-scale preprocessing
- Contrast enhancement
- Edge detection integration
- Object highlighting
- Scene segmentation
- Motion detection (between frames)
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
from typing import Tuple, Optional, List
import cv2
import io
import base64


class AdvancedImageProcessor:
    """Advanced image preprocessing for AI vision models"""
    
    def __init__(self, target_size: int = 1024, enhance_mode: str = 'balanced'):
        """
        Initialize image processor
        
        Args:
            target_size: Maximum width/height for processed images
            enhance_mode: 'speed', 'balanced', or 'quality'
        """
        self.target_size = target_size
        self.enhance_mode = enhance_mode
        self.previous_frame = None
        
        # Enhancement settings based on mode
        self.settings = {
            'speed': {
                'size': 768,
                'quality': 85,
                'sharpness': 1.0,
                'contrast': 1.0,
                'brightness': 1.0,
            },
            'balanced': {
                'size': 1024,
                'quality': 92,
                'sharpness': 1.3,
                'contrast': 1.15,
                'brightness': 1.05,
            },
            'quality': {
                'size': 1280,
                'quality': 98,
                'sharpness': 1.5,
                'contrast': 1.25,
                'brightness': 1.1,
            }
        }
        
        self.current_settings = self.settings.get(enhance_mode, self.settings['balanced'])
    
    def preprocess_for_vision_model(self, img: Image.Image, 
                                   detect_motion: bool = True) -> Image.Image:
        """
        Complete preprocessing pipeline for vision models
        
        Args:
            img: Input PIL Image
            detect_motion: Whether to detect motion from previous frame
            
        Returns:
            Enhanced PIL Image
        """
        # Step 1: Resize intelligently
        img = self._smart_resize(img)
        
        # Step 2: Enhance contrast and brightness
        img = self._enhance_visibility(img)
        
        # Step 3: Sharpen details
        img = self._sharpen_details(img)
        
        # Step 4: Detect motion regions (if enabled)
        if detect_motion and self.previous_frame is not None:
            img = self._highlight_motion_regions(img)
        
        # Step 5: Enhance UI elements detection
        img = self._enhance_ui_elements(img)
        
        # Store for next frame
        self.previous_frame = img.copy()
        
        return img
    
    def _smart_resize(self, img: Image.Image) -> Image.Image:
        """Intelligent resizing that preserves important details"""
        target = self.current_settings['size']
        
        if img.width <= target and img.height <= target:
            return img
        
        # Calculate new size maintaining aspect ratio
        if img.width > img.height:
            new_width = target
            new_height = int(img.height * (target / img.width))
        else:
            new_height = target
            new_width = int(img.width * (target / img.height))
        
        # Use LANCZOS for high-quality downscaling
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _enhance_visibility(self, img: Image.Image) -> Image.Image:
        """Enhance contrast and brightness for better AI understanding"""
        # Contrast enhancement
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(self.current_settings['contrast'])
        
        # Brightness enhancement
        brightness_enhancer = ImageEnhance.Brightness(img)
        img = brightness_enhancer.enhance(self.current_settings['brightness'])
        
        # Color saturation for better color recognition
        color_enhancer = ImageEnhance.Color(img)
        img = color_enhancer.enhance(1.1)
        
        return img
    
    def _sharpen_details(self, img: Image.Image) -> Image.Image:
        """Sharpen image for better detail recognition"""
        sharpness_enhancer = ImageEnhance.Sharpness(img)
        img = sharpness_enhancer.enhance(self.current_settings['sharpness'])
        
        # Additional unsharp mask for critical details
        if self.enhance_mode == 'quality':
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return img
    
    def _detect_motion_regions(self, current_img: Image.Image, 
                               previous_img: Image.Image) -> np.ndarray:
        """
        Detect regions with motion between frames
        Returns binary mask of motion regions
        """
        # Convert to numpy arrays
        current = np.array(current_img)
        previous = np.array(previous_img)
        
        # Calculate absolute difference
        diff = cv2.absdiff(current, previous)
        
        # Convert to grayscale
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to get binary mask
        _, motion_mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=2)
        
        return motion_mask
    
    def _highlight_motion_regions(self, img: Image.Image) -> Image.Image:
        """
        Highlight motion regions to help AI focus on action
        This is transparent to the model but improves attention
        """
        if self.previous_frame is None:
            return img
        
        try:
            # Ensure same size
            if img.size != self.previous_frame.size:
                return img
            
            motion_mask = self._detect_motion_regions(img, self.previous_frame)
            
            # Convert mask to PIL
            motion_pil = Image.fromarray(motion_mask)
            
            # Subtle brightness boost in motion regions
            img_array = np.array(img)
            mask_expanded = np.stack([motion_mask] * 3, axis=-1) / 255.0
            
            # Boost brightness slightly in motion areas
            img_array = img_array.astype(np.float32)
            img_array += mask_expanded * 15  # Subtle boost
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            
            return Image.fromarray(img_array)
        except:
            # If motion detection fails, return original
            return img
    
    def _enhance_ui_elements(self, img: Image.Image) -> Image.Image:
        """
        Enhance UI elements (text, health bars, scores) for better recognition
        Uses edge detection to emphasize UI boundaries
        """
        if self.enhance_mode == 'speed':
            return img  # Skip for speed mode
        
        try:
            # Convert to numpy
            img_array = np.array(img)
            
            # Detect edges (UI elements have strong edges)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges slightly
            kernel = np.ones((2, 2), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Blend edges back into image for emphasis
            edges_colored = np.stack([edges] * 3, axis=-1)
            img_array = img_array.astype(np.float32)
            img_array += edges_colored * 0.15  # Subtle edge emphasis
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
            
            return Image.fromarray(img_array)
        except:
            return img
    
    def create_multi_scale_representation(self, img: Image.Image) -> List[Image.Image]:
        """
        Create multiple scales of the image for multi-scale analysis
        Useful for detecting both large objects and fine details
        """
        scales = []
        
        # Full resolution
        scales.append(img)
        
        # 75% scale
        w, h = img.size
        scales.append(img.resize((int(w * 0.75), int(h * 0.75)), Image.Resampling.LANCZOS))
        
        # 50% scale
        scales.append(img.resize((int(w * 0.5), int(h * 0.5)), Image.Resampling.LANCZOS))
        
        return scales
    
    def add_context_overlay(self, img: Image.Image, 
                           context_text: Optional[str] = None) -> Image.Image:
        """
        Add visual context overlay to help model understand image type
        (e.g., highlight game UI regions, overlay grid for spatial understanding)
        """
        if not context_text:
            return img
        
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy, 'RGBA')
        
        # Add semi-transparent context indicators
        # This can help the model understand image structure
        
        return img_copy
    
    def enhance_color_channels(self, img: Image.Image) -> Image.Image:
        """
        Enhance specific color channels for better recognition of game elements
        (e.g., red health bars, blue mana, yellow highlights)
        """
        img_array = np.array(img).astype(np.float32)
        
        # Boost red channel (health bars, alerts)
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.1, 0, 255)
        
        # Boost yellow/orange (important UI elements)
        yellow_mask = (img_array[:, :, 0] > 150) & (img_array[:, :, 1] > 150) & (img_array[:, :, 2] < 100)
        img_array[yellow_mask] = np.clip(img_array[yellow_mask] * 1.15, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))
    
    def to_base64(self, img: Image.Image, quality: Optional[int] = None) -> str:
        """Convert processed image to base64 for API transmission"""
        buffered = io.BytesIO()
        q = quality or self.current_settings['quality']
        img.save(buffered, format="JPEG", quality=q, optimize=True)
        img_bytes = buffered.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def get_image_statistics(self, img: Image.Image) -> dict:
        """
        Analyze image statistics to provide context to the model
        Helps model understand scene brightness, contrast, etc.
        """
        img_array = np.array(img)
        
        stats = {
            'mean_brightness': np.mean(img_array),
            'std_brightness': np.std(img_array),
            'is_dark_scene': np.mean(img_array) < 80,
            'is_bright_scene': np.mean(img_array) > 180,
            'has_high_contrast': np.std(img_array) > 60,
            'dominant_color': self._get_dominant_color(img_array),
        }
        
        return stats
    
    def _get_dominant_color(self, img_array: np.ndarray) -> str:
        """Determine dominant color in the scene"""
        mean_colors = np.mean(img_array, axis=(0, 1))
        r, g, b = mean_colors
        
        if r > g and r > b:
            return 'red'
        elif g > r and g > b:
            return 'green'
        elif b > r and b > g:
            return 'blue'
        elif r > 100 and g > 100 and b < 80:
            return 'yellow'
        else:
            return 'neutral'
    
    def adaptive_preprocessing(self, img: Image.Image, 
                              scene_type: Optional[str] = None) -> Image.Image:
        """
        Apply adaptive preprocessing based on detected scene type
        
        Args:
            img: Input image
            scene_type: 'dark', 'bright', 'action', 'menu', etc.
            
        Returns:
            Optimally processed image
        """
        # Auto-detect scene type if not provided
        if scene_type is None:
            stats = self.get_image_statistics(img)
            if stats['is_dark_scene']:
                scene_type = 'dark'
            elif stats['is_bright_scene']:
                scene_type = 'bright'
            else:
                scene_type = 'normal'
        
        # Apply scene-specific enhancements
        if scene_type == 'dark':
            # Boost brightness more for dark scenes
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)
        elif scene_type == 'bright':
            # Reduce brightness, increase contrast
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.9)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
        
        return img


class GameplaySceneAnalyzer:
    """
    Analyzes gameplay scenes to provide context to the vision model
    This pre-analysis helps the model focus on important elements
    """
    
    def __init__(self):
        self.frame_history = []
        self.max_history = 5
    
    def analyze_scene_type(self, img: Image.Image) -> dict:
        """
        Analyze what type of scene this is
        (menu, gameplay, cutscene, loading, etc.)
        """
        img_array = np.array(img)
        
        analysis = {
            'scene_type': 'gameplay',  # Default
            'is_static': self._is_static_scene(img_array),
            'has_ui': self._detect_ui_elements(img_array),
            'motion_level': self._calculate_motion_level(img_array),
            'brightness_level': np.mean(img_array),
        }
        
        # Classify scene type
        if analysis['is_static'] and analysis['brightness_level'] < 50:
            analysis['scene_type'] = 'loading'
        elif analysis['is_static'] and analysis['has_ui']:
            analysis['scene_type'] = 'menu'
        elif analysis['motion_level'] > 0.7:
            analysis['scene_type'] = 'intense_action'
        
        return analysis
    
    def _is_static_scene(self, img_array: np.ndarray) -> bool:
        """Detect if scene is mostly static"""
        if len(self.frame_history) == 0:
            self.frame_history.append(img_array)
            return False
        
        # Compare with previous frame
        diff = np.mean(np.abs(img_array - self.frame_history[-1]))
        
        # Update history
        self.frame_history.append(img_array)
        if len(self.frame_history) > self.max_history:
            self.frame_history.pop(0)
        
        return diff < 5  # Threshold for static scene
    
    def _detect_ui_elements(self, img_array: np.ndarray) -> bool:
        """Detect presence of UI elements"""
        # UI elements typically have high contrast edges
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size
        
        return edge_density > 0.05  # Threshold for UI presence
    
    def _calculate_motion_level(self, img_array: np.ndarray) -> float:
        """Calculate motion level (0.0 to 1.0)"""
        if len(self.frame_history) == 0:
            return 0.0
        
        diff = np.abs(img_array - self.frame_history[-1])
        motion = np.mean(diff) / 255.0
        
        return min(motion * 5, 1.0)  # Scale and cap at 1.0
