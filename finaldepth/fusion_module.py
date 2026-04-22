"""
Fusion module that combines object detection with depth data
"""
import numpy as np
from config import DISTANCE_ZONES, FRAME_WIDTH, FRAME_HEIGHT

class FusionModule:
    def __init__(self):
        self.frame_width = FRAME_WIDTH
        self.frame_height = FRAME_HEIGHT
        
    def fuse_detection_depth(self, detections, depth_map, depth_estimator):
        """
        Combine object detections with depth information
        Returns: Enhanced detections with spatial context
        """
        enhanced_detections = []
        
        for detection in detections:
            enhanced = detection.copy()
            
            # Get distance for this object
            distance = depth_estimator.get_object_distance(
                depth_map, 
                detection['center'], 
                detection['bbox']
            )
            
            if distance is not None:
                enhanced['distance'] = distance
                enhanced['distance_zone'] = self._get_distance_zone(distance)
                enhanced['spatial_context'] = self._get_spatial_context(detection, distance)
                enhanced['location_description'] = self._get_location_description(detection['center'])
                enhanced['navigation_priority'] = self._calculate_priority(detection, distance)
            else:
                enhanced['distance'] = None
                enhanced['distance_zone'] = 'unknown'
                enhanced['spatial_context'] = 'distance unknown'
                enhanced['location_description'] = self._get_location_description(detection['center'])
                enhanced['navigation_priority'] = 0
            
            enhanced_detections.append(enhanced)
        
        # Sort by navigation priority (highest first)
        enhanced_detections.sort(key=lambda x: x['navigation_priority'], reverse=True)
        
        return enhanced_detections
    
    def _get_distance_zone(self, distance):
        """Categorize distance into zones"""
        for zone, (min_dist, max_dist) in DISTANCE_ZONES.items():
            if min_dist <= distance < max_dist:
                return zone
        return 'unknown'
    
    def _get_spatial_context(self, detection, distance):
        """Generate spatial context description"""
        obj_class = detection['class']
        zone = self._get_distance_zone(distance)
        location = self._get_location_description(detection['center'])
        
        # Generate context based on distance and object type
        if zone == 'immediate':
            if obj_class == 'person':
                context = "very close, immediate attention needed"
            else:
                context = "very close, potential obstacle"
        elif zone == 'close':
            if obj_class in ['person', 'chair', 'couch']:
                context = "nearby, may block your path"
            else:
                context = "close by, be aware"
        elif zone == 'medium':
            context = "at medium distance, monitor"
        else:
            context = "far away, low priority"
        
        return context
    
    def _get_location_description(self, center_point):
        """Get relative location description (left, center, right)"""
        x, y = center_point
        
        # Horizontal position
        if x < self.frame_width * 0.33:
            h_pos = "left"
        elif x < self.frame_width * 0.67:
            h_pos = "center"
        else:
            h_pos = "right"
        
        # Vertical position
        if y < self.frame_height * 0.33:
            v_pos = "upper"
        elif y < self.frame_height * 0.67:
            v_pos = "middle"
        else:
            v_pos = "lower"
        
        # Combine for natural description
        if h_pos == "center":
            return f"{v_pos} center"
        else:
            return f"{v_pos}-{h_pos}"
    
    def _calculate_priority(self, detection, distance):
        """Calculate navigation priority score"""
        base_priority = 0
        
        # Priority based on object type
        if detection['priority']:  # Priority objects from config
            base_priority += 50
        
        # Priority based on distance (closer = higher priority)
        if distance is not None:
            if distance < 1.5:
                base_priority += 100  # Immediate attention
            elif distance < 3.0:
                base_priority += 75   # High priority
            elif distance < 6.0:
                base_priority += 25   # Medium priority
            # Far objects get no distance bonus
        
        # Priority based on location (center objects more important)
        center_x = detection['center'][0]
        center_distance = abs(center_x - self.frame_width / 2)
        center_factor = 1 - (center_distance / (self.frame_width / 2))
        base_priority += int(center_factor * 25)
        
        # Confidence factor
        base_priority += int(detection['confidence'] * 10)
        
        return base_priority
    
    def get_navigation_summary(self, enhanced_detections, max_objects=3):
        """
        Generate navigation summary for top priority objects
        """
        # Filter for objects with distance info and high priority
        priority_objects = [
            det for det in enhanced_detections 
            if det['distance'] is not None and det['navigation_priority'] > 25
        ]
        
        # Take top objects
        top_objects = priority_objects[:max_objects]
        
        summary = {
            'total_objects': len(enhanced_detections),
            'priority_objects': len(priority_objects),
            'immediate_threats': len([d for d in priority_objects if d['distance_zone'] == 'immediate']),
            'close_objects': len([d for d in priority_objects if d['distance_zone'] == 'close']),
            'top_objects': top_objects
        }
        
        return summary