"""
Advanced depth visualization with 3D measurements and enhanced UI
"""
import cv2
import numpy as np
import time
import math
from typing import List, Dict, Tuple

class AdvancedVisualizer:
    def __init__(self):
        self.colors = {
            'person': (255, 20, 147),      # Deep Pink/Magenta
            'vehicle': (0, 100, 255),      # Orange-Red  
            'furniture': (0, 255, 255),    # Cyan
            'electronics': (255, 255, 0),  # Yellow
            'default': (255, 255, 255)     # White
        }
        
        # Enhanced depth colormap
        self.depth_colormap = cv2.COLORMAP_PLASMA  # Vibrant plasma colors
        
        # Animation state
        self.animation_time = 0
        self.pulse_phase = 0
        
        # UI styling
        self.ui_font = cv2.FONT_HERSHEY_DUPLEX
        self.title_font = cv2.FONT_HERSHEY_TRIPLEX
        
    def create_enhanced_depth_view(self, frame, depth_map, detections):
        """
        Create enhanced depth visualization with cinematic effects
        """
        if depth_map is None:
            return self._create_fallback_view(frame, detections)
            
        # Update animation state
        self.animation_time = time.time()
        self.pulse_phase = (self.animation_time * 2) % (2 * math.pi)
        
        # Resize depth map to match frame
        h, w = frame.shape[:2]
        depth_resized = cv2.resize(depth_map, (w, h))
        
        # Apply enhanced colormap with dynamic contrast
        depth_colored = cv2.applyColorMap(depth_resized, self.depth_colormap)
        
        # Add subtle glow effect to depth map
        depth_glow = cv2.GaussianBlur(depth_colored, (15, 15), 0)
        depth_enhanced = cv2.addWeighted(depth_colored, 0.8, depth_glow, 0.2, 0)
        
        # Blend with original frame for semi-transparent effect
        alpha = 0.75  # Slightly more depth map visibility
        blended = cv2.addWeighted(depth_enhanced, alpha, frame, 1-alpha, 0)
        
        # Add subtle vignette effect
        blended = self._add_vignette(blended)
        
        # Draw enhanced detection overlays
        enhanced_frame = self._draw_enhanced_detections(blended, detections, depth_resized)
        
        return enhanced_frame
    
    def _create_fallback_view(self, frame, detections):
        """Create stylized view when depth map is unavailable"""
        # Apply subtle color grading
        enhanced = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
        
        # Add blue tint for tech aesthetic
        blue_tint = np.zeros_like(enhanced)
        blue_tint[:, :, 0] = 20  # Add blue channel
        enhanced = cv2.addWeighted(enhanced, 0.9, blue_tint, 0.1, 0)
        
        # Draw detections
        enhanced = self._draw_enhanced_detections(enhanced, detections, None)
        
        return enhanced
    
    def _draw_enhanced_detections(self, frame, detections, depth_map):
        """Draw enhanced detection boxes with cinematic 3D measurements"""
        
        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class']
            distance = detection.get('distance', 0)
            center_x, center_y = detection['center']
            priority = detection.get('navigation_priority', 0)
            
            # Get color based on object type
            base_color = self._get_object_color(class_name)
            
            # Add pulsing effect for high priority objects
            if priority > 75:
                pulse_intensity = abs(math.sin(self.pulse_phase)) * 0.3 + 0.7
                color = tuple(int(c * pulse_intensity) for c in base_color)
            else:
                color = base_color
            
            # Draw animated scanning lines
            self._draw_scanning_effect(frame, (x1, y1, x2, y2), color, i)
            
            # Draw main bounding box with gradient effect
            self._draw_gradient_box(frame, (x1, y1, x2, y2), color, priority)
            
            # Draw futuristic corner markers
            corner_size = 20
            self._draw_futuristic_corners(frame, (x1, y1, x2, y2), color, corner_size)
            
            # Create sleek label with glow effect
            self._draw_sleek_label(frame, class_name, (x1, y1), color)
            
            # Draw 3D distance measurement with enhanced styling
            if distance and distance > 0:
                self._draw_enhanced_3d_measurement(frame, center_x, center_y, distance, depth_map, color)
            
            # Draw animated crosshair
            self._draw_animated_crosshair(frame, center_x, center_y, color)
            
            # Add object trail effect for moving objects
            self._draw_motion_trail(frame, detection, color)
        
        return frame
    
    def _get_object_color(self, class_name):
        """Get color based on object category with enhanced categorization"""
        if class_name == 'person':
            return self.colors['person']
        elif class_name in ['car', 'truck', 'bus', 'motorcycle', 'bicycle']:
            return self.colors['vehicle']
        elif class_name in ['chair', 'couch', 'bed', 'dining table']:
            return self.colors['furniture']
        elif class_name in ['laptop', 'mouse', 'keyboard', 'cell phone', 'tv']:
            return self.colors['electronics']
        else:
            return self.colors['default']
    
    def _add_vignette(self, frame):
        """Add subtle vignette effect for cinematic look"""
        h, w = frame.shape[:2]
        
        # Create vignette mask
        center_x, center_y = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        
        # Normalize distance
        max_dist = np.sqrt(center_x**2 + center_y**2)
        normalized_dist = dist_from_center / max_dist
        
        # Create vignette (darker at edges)
        vignette = 1 - (normalized_dist * 0.3)
        vignette = np.clip(vignette, 0.7, 1.0)
        
        # Apply vignette
        for i in range(3):
            frame[:, :, i] = frame[:, :, i] * vignette
        
        return frame
    
    def _draw_scanning_effect(self, frame, bbox, color, index):
        """Draw animated scanning lines across objects"""
        x1, y1, x2, y2 = bbox
        
        # Calculate scanning line position based on time and object index
        scan_speed = 2.0
        scan_offset = (self.animation_time * scan_speed + index * 0.5) % 2.0
        
        if scan_offset < 1.0:
            # Horizontal scan
            scan_y = int(y1 + (y2 - y1) * scan_offset)
            if y1 <= scan_y <= y2:
                cv2.line(frame, (x1, scan_y), (x2, scan_y), color, 2)
                # Add glow effect
                cv2.line(frame, (x1, scan_y), (x2, scan_y), (255, 255, 255), 1)
    
    def _draw_gradient_box(self, frame, bbox, color, priority):
        """Draw bounding box with gradient effect"""
        x1, y1, x2, y2 = bbox
        
        # Base thickness based on priority
        thickness = 4 if priority > 75 else 3 if priority > 50 else 2
        
        # Draw main box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        
        # Add inner glow
        inner_color = tuple(min(255, int(c * 1.5)) for c in color)
        cv2.rectangle(frame, (x1+1, y1+1), (x2-1, y2-1), inner_color, 1)
    
    def _draw_futuristic_corners(self, frame, bbox, color, size):
        """Draw futuristic corner markers with enhanced styling"""
        x1, y1, x2, y2 = bbox
        thickness = 4
        
        # Enhanced corner design
        corner_length = size
        
        # Top-left corner
        cv2.line(frame, (x1, y1), (x1 + corner_length, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_length), color, thickness)
        # Add inner accent
        cv2.line(frame, (x1+2, y1+2), (x1 + corner_length-2, y1+2), (255, 255, 255), 1)
        cv2.line(frame, (x1+2, y1+2), (x1+2, y1 + corner_length-2), (255, 255, 255), 1)
        
        # Top-right corner  
        cv2.line(frame, (x2, y1), (x2 - corner_length, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_length), color, thickness)
        cv2.line(frame, (x2-2, y1+2), (x2 - corner_length+2, y1+2), (255, 255, 255), 1)
        cv2.line(frame, (x2-2, y1+2), (x2-2, y1 + corner_length-2), (255, 255, 255), 1)
        
        # Bottom-left corner
        cv2.line(frame, (x1, y2), (x1 + corner_length, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_length), color, thickness)
        cv2.line(frame, (x1+2, y2-2), (x1 + corner_length-2, y2-2), (255, 255, 255), 1)
        cv2.line(frame, (x1+2, y2-2), (x1+2, y2 - corner_length+2), (255, 255, 255), 1)
        
        # Bottom-right corner
        cv2.line(frame, (x2, y2), (x2 - corner_length, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_length), color, thickness)
        cv2.line(frame, (x2-2, y2-2), (x2 - corner_length+2, y2-2), (255, 255, 255), 1)
        cv2.line(frame, (x2-2, y2-2), (x2-2, y2 - corner_length+2), (255, 255, 255), 1)
    
    def _draw_sleek_label(self, frame, text, position, color):
        """Draw sleek label with glow effect"""
        x, y = position
        
        # Calculate text size
        font_scale = 0.9
        thickness = 2
        text_size = cv2.getTextSize(text, self.ui_font, font_scale, thickness)[0]
        
        # Create label background with rounded corners effect
        padding = 12
        label_width = text_size[0] + padding * 2
        label_height = 40
        
        # Draw background with gradient effect
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y-label_height), (x + label_width, y), color, -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Draw border
        cv2.rectangle(frame, (x, y-label_height), (x + label_width, y), (255, 255, 255), 2)
        
        # Draw text with glow effect
        text_x = x + padding
        text_y = y - 12
        
        # Glow effect (multiple passes)
        for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            cv2.putText(frame, text, (text_x + offset[0], text_y + offset[1]), 
                       self.ui_font, font_scale, (255, 255, 255), 1)
        
        # Main text
        cv2.putText(frame, text, (text_x, text_y), 
                   self.ui_font, font_scale, (0, 0, 0), thickness)
    
    def _draw_corner_markers(self, frame, bbox, color, size):
        """Draw corner markers for modern bounding box look"""
        x1, y1, x2, y2 = bbox
        thickness = 3
        
        # Top-left corner
        cv2.line(frame, (x1, y1), (x1 + size, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + size), color, thickness)
        
        # Top-right corner  
        cv2.line(frame, (x2, y1), (x2 - size, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + size), color, thickness)
        
        # Bottom-left corner
        cv2.line(frame, (x1, y2), (x1 + size, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x1, y2 - size), color, thickness)
        
        # Bottom-right corner
        cv2.line(frame, (x2, y2), (x2 - size, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - size), color, thickness)
    
    def _draw_enhanced_3d_measurement(self, frame, x, y, distance, depth_map, color):
        """Draw enhanced 3D distance measurement with cinematic styling"""
        
        # Get pixel depth value at center point
        if depth_map is not None:
            h, w = depth_map.shape
            if 0 <= x < w and 0 <= y < h:
                pixel_depth = depth_map[y, x]
            else:
                pixel_depth = 0
        else:
            pixel_depth = 0
        
        # Create measurement texts with enhanced formatting
        measurement_text = f"3D: {distance:.1f}m"
        pixel_text = f"Pixel: {pixel_depth}px"
        
        # Calculate text sizes
        font_scale = 0.7
        thickness = 2
        
        text1_size = cv2.getTextSize(measurement_text, self.ui_font, font_scale, thickness)[0]
        text2_size = cv2.getTextSize(pixel_text, self.ui_font, font_scale, thickness)[0]
        
        # Enhanced box dimensions
        box_width = max(text1_size[0], text2_size[0]) + 30
        box_height = 60
        
        # Position box (top-right of screen with offset)
        box_x = frame.shape[1] - box_width - 15
        box_y = 15
        
        # Draw enhanced background with glow effect
        overlay = frame.copy()
        
        # Main background
        bg_color = (80, 0, 80)  # Dark purple
        cv2.rectangle(overlay, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     bg_color, -1)
        
        # Glow effect
        glow_overlay = frame.copy()
        cv2.rectangle(glow_overlay, (box_x-5, box_y-5), (box_x + box_width+5, box_y + box_height+5), 
                     color, -1)
        cv2.GaussianBlur(glow_overlay, (15, 15), 0, glow_overlay)
        cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0, frame)
        
        # Apply main background
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        # Draw animated border
        border_color = tuple(int(c * (0.8 + 0.2 * abs(math.sin(self.pulse_phase)))) for c in color)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), 
                     border_color, 3)
        
        # Add corner accents
        accent_size = 8
        cv2.line(frame, (box_x, box_y), (box_x + accent_size, box_y), (0, 255, 0), 3)
        cv2.line(frame, (box_x, box_y), (box_x, box_y + accent_size), (0, 255, 0), 3)
        cv2.line(frame, (box_x + box_width, box_y + box_height), (box_x + box_width - accent_size, box_y + box_height), (0, 255, 0), 3)
        cv2.line(frame, (box_x + box_width, box_y + box_height), (box_x + box_width, box_y + box_height - accent_size), (0, 255, 0), 3)
        
        # Draw text with enhanced styling
        text_color = (0, 255, 0)  # Bright green
        
        # Distance text
        cv2.putText(frame, measurement_text, (box_x + 15, box_y + 25), 
                   self.ui_font, font_scale, text_color, thickness)
        
        # Pixel text
        cv2.putText(frame, pixel_text, (box_x + 15, box_y + 50), 
                   self.ui_font, font_scale, text_color, thickness)
        
        # Draw animated connection line
        line_color = tuple(int(c * (0.7 + 0.3 * abs(math.sin(self.pulse_phase * 2)))) for c in color)
        cv2.line(frame, (x, y), (box_x, box_y + box_height//2), line_color, 3)
        
        # Add line glow
        cv2.line(frame, (x, y), (box_x, box_y + box_height//2), (255, 255, 255), 1)
    
    def _draw_animated_crosshair(self, frame, x, y, color):
        """Draw animated crosshair with pulsing effect"""
        # Pulsing size based on animation
        base_size = 12
        pulse_size = int(base_size + 4 * abs(math.sin(self.pulse_phase * 3)))
        thickness = 3
        
        # Animated color
        pulse_intensity = abs(math.sin(self.pulse_phase * 2)) * 0.5 + 0.5
        animated_color = tuple(int(c * pulse_intensity + 255 * (1 - pulse_intensity)) for c in color)
        
        # Draw crosshair with glow
        # Horizontal line
        cv2.line(frame, (x - pulse_size, y), (x + pulse_size, y), animated_color, thickness)
        cv2.line(frame, (x - pulse_size, y), (x + pulse_size, y), (255, 255, 255), 1)
        
        # Vertical line  
        cv2.line(frame, (x, y - pulse_size), (x, y + pulse_size), animated_color, thickness)
        cv2.line(frame, (x, y - pulse_size), (x, y + pulse_size), (255, 255, 255), 1)
        
        # Center dot with pulsing
        center_size = int(4 + 2 * abs(math.sin(self.pulse_phase * 4)))
        cv2.circle(frame, (x, y), center_size, animated_color, -1)
        cv2.circle(frame, (x, y), 2, (255, 255, 255), -1)
    
    def _draw_motion_trail(self, frame, detection, color):
        """Draw motion trail effect for moving objects"""
        # This would require tracking object positions over time
        # For now, just add a subtle glow around the object
        x1, y1, x2, y2 = detection['bbox']
        
        # Create glow effect
        glow_overlay = frame.copy()
        cv2.rectangle(glow_overlay, (x1-10, y1-10), (x2+10, y2+10), color, -1)
        glow_blurred = cv2.GaussianBlur(glow_overlay, (21, 21), 0)
        cv2.addWeighted(glow_blurred, 0.1, frame, 0.9, 0, frame)
    
    def _draw_crosshair(self, frame, x, y, color):
        """Draw center crosshair"""
        size = 10
        thickness = 2
        
        # Horizontal line
        cv2.line(frame, (x - size, y), (x + size, y), color, thickness)
        # Vertical line  
        cv2.line(frame, (x, y - size), (x, y + size), color, thickness)
        # Center dot
        cv2.circle(frame, (x, y), 3, color, -1)
    
    def add_enhanced_ui(self, frame, system_info):
        """Add cinematic enhanced UI elements"""
        h, w = frame.shape[:2]
        
        # Add sophisticated gradient overlay
        self._add_ui_gradient(frame, h, w)
        
        # Enhanced system info with futuristic styling
        self._draw_system_status(frame, system_info, w)
        
        # Add HUD-style elements
        self._draw_hud_elements(frame, h, w)
        
        # Enhanced controls at bottom with better styling
        self._draw_enhanced_controls(frame, h, w)
        
        return frame
    
    def _add_ui_gradient(self, frame, h, w):
        """Add sophisticated gradient overlays"""
        # Top gradient
        overlay = frame.copy()
        for i in range(100):
            alpha = (100 - i) / 100 * 0.4
            color_intensity = int(alpha * 255)
            cv2.line(overlay, (0, i), (w, i), (0, 0, color_intensity), 1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Bottom gradient
        overlay = frame.copy()
        for i in range(60):
            alpha = i / 60 * 0.3
            color_intensity = int(alpha * 255)
            cv2.line(overlay, (0, h-60+i), (w, h-60+i), (0, 0, color_intensity), 1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    def _draw_system_status(self, frame, system_info, w):
        """Draw system status with enhanced styling"""
        # Status panel background
        panel_width = 300
        panel_height = 80
        panel_x = 20
        panel_y = 10
        
        # Draw panel background with glow
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), 
                     (20, 20, 40), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Panel border with animated glow
        border_intensity = abs(math.sin(self.pulse_phase)) * 0.3 + 0.7
        border_color = (int(0 * border_intensity), int(255 * border_intensity), int(255 * border_intensity))
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), 
                     border_color, 2)
        
        # System title
        title_text = "ENHANCED VISION SYSTEM"
        cv2.putText(frame, title_text, (panel_x + 10, panel_y + 20), 
                   self.ui_font, 0.5, (0, 255, 255), 1)
        
        # Object count with enhanced styling
        objects_count = system_info.get('objects', 0)
        objects_text = f"TARGETS: {objects_count:02d}"
        cv2.putText(frame, objects_text, (panel_x + 10, panel_y + 40), 
                   self.ui_font, 0.6, (0, 255, 0), 2)
        
        # Audio status with color coding
        speaking = system_info.get('speaking', False)
        audio_color = (0, 255, 255) if speaking else (100, 100, 100)
        audio_text = "AUDIO: ACTIVE" if speaking else "AUDIO: STANDBY"
        cv2.putText(frame, audio_text, (panel_x + 10, panel_y + 60), 
                   self.ui_font, 0.5, audio_color, 1)
        
        # FPS counter with performance color coding
        fps = system_info.get('fps', 0)
        fps_color = (0, 255, 0) if fps > 15 else (0, 255, 255) if fps > 10 else (0, 0, 255)
        fps_text = f"FPS: {fps:05.1f}"
        fps_size = cv2.getTextSize(fps_text, self.ui_font, 0.6, 2)[0]
        cv2.putText(frame, fps_text, (w - fps_size[0] - 20, 40), 
                   self.ui_font, 0.6, fps_color, 2)
    
    def _draw_hud_elements(self, frame, h, w):
        """Draw HUD-style elements"""
        # Corner brackets
        bracket_size = 30
        bracket_color = (0, 255, 255)
        
        # Top-left
        cv2.line(frame, (10, 10), (10 + bracket_size, 10), bracket_color, 2)
        cv2.line(frame, (10, 10), (10, 10 + bracket_size), bracket_color, 2)
        
        # Top-right
        cv2.line(frame, (w-10, 10), (w-10-bracket_size, 10), bracket_color, 2)
        cv2.line(frame, (w-10, 10), (w-10, 10 + bracket_size), bracket_color, 2)
        
        # Bottom-left
        cv2.line(frame, (10, h-10), (10 + bracket_size, h-10), bracket_color, 2)
        cv2.line(frame, (10, h-10), (10, h-10-bracket_size), bracket_color, 2)
        
        # Bottom-right
        cv2.line(frame, (w-10, h-10), (w-10-bracket_size, h-10), bracket_color, 2)
        cv2.line(frame, (w-10, h-10), (w-10, h-10-bracket_size), bracket_color, 2)
        
        # Center crosshair
        center_x, center_y = w // 2, h // 2
        cross_size = 20
        cv2.line(frame, (center_x - cross_size, center_y), (center_x + cross_size, center_y), 
                (255, 255, 255), 1)
        cv2.line(frame, (center_x, center_y - cross_size), (center_x, center_y + cross_size), 
                (255, 255, 255), 1)
        cv2.circle(frame, (center_x, center_y), 3, (255, 255, 255), 1)
    
    def _draw_enhanced_controls(self, frame, h, w):
        """Draw enhanced control panel"""
        controls_text = "Q:QUIT | D:DEPTH | S:SILENCE | C:CLEAR | M:MODE | T:TEST | R:RESET"
        
        # Calculate text size
        text_size = cv2.getTextSize(controls_text, self.ui_font, 0.5, 1)[0]
        
        # Control panel dimensions
        panel_width = text_size[0] + 40
        panel_height = 35
        panel_x = (w - panel_width) // 2
        panel_y = h - panel_height - 10
        
        # Draw panel background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Panel border
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), 
                     (0, 255, 255), 2)
        
        # Control text
        cv2.putText(frame, controls_text, (panel_x + 20, panel_y + 22), 
                   self.ui_font, 0.5, (255, 255, 255), 1)
    
    def create_split_view(self, original_frame, depth_frame, detections):
        """Create side-by-side view like reference image"""
        
        # Ensure both frames are same height
        h = min(original_frame.shape[0], depth_frame.shape[0])
        original_resized = cv2.resize(original_frame, (original_frame.shape[1], h))
        depth_resized = cv2.resize(depth_frame, (depth_frame.shape[1], h))
        
        # Create side-by-side view
        combined = cv2.hconcat([original_resized, depth_resized])
        
        # Add separator line
        separator_x = original_resized.shape[1]
        cv2.line(combined, (separator_x, 0), (separator_x, h), (255, 255, 255), 2)
        
        return combined