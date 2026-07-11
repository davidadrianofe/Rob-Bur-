#!/usr/bin/env python3
"""Movement Tracking System

Author: David Adriano Ferrari dos Santos
Description: Tracks and monitors robot movement in real-time
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import math
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrackPoint:
    """Single tracking point"""
    timestamp: float
    x: float
    y: float
    angle: float
    velocity_linear: float
    velocity_angular: float


class MovementTracker:
    """Tracks robot movement with AI analysis"""
    
    def __init__(self, max_history: int = 1000):
        """Initialize movement tracker
        
        Args:
            max_history: Maximum tracking points to keep
        """
        self.tracking_history: deque = deque(maxlen=max_history)
        self.max_history = max_history
        self.total_distance = 0.0
        self.total_time = 0.0
        self.average_speed = 0.0
        self.max_speed = 0.0
        
        logger.info(f"Movement tracker initialized (max history: {max_history})")
    
    def add_track_point(
        self,
        timestamp: float,
        x: float,
        y: float,
        angle: float,
        velocity_linear: float = 0.0,
        velocity_angular: float = 0.0,
    ):
        """Add tracking point
        
        Args:
            timestamp: Timestamp
            x: X coordinate
            y: Y coordinate
            angle: Angle in radians
            velocity_linear: Linear velocity
            velocity_angular: Angular velocity
        """
        point = TrackPoint(
            timestamp=timestamp,
            x=x,
            y=y,
            angle=angle,
            velocity_linear=velocity_linear,
            velocity_angular=velocity_angular,
        )
        
        self.tracking_history.append(point)
        self._update_statistics()
    
    def _update_statistics(self):
        """Update tracking statistics"""
        if len(self.tracking_history) < 2:
            return
        
        points = list(self.tracking_history)
        
        # Calculate total distance
        self.total_distance = 0.0
        for i in range(1, len(points)):
            dx = points[i].x - points[i-1].x
            dy = points[i].y - points[i-1].y
            self.total_distance += math.sqrt(dx**2 + dy**2)
        
        # Calculate total time
        self.total_time = points[-1].timestamp - points[0].timestamp
        
        # Calculate average speed
        if self.total_time > 0:
            self.average_speed = self.total_distance / self.total_time
        
        # Calculate max speed
        self.max_speed = max(
            (p.velocity_linear for p in points),
            default=0.0
        )
    
    def get_trajectory(self) -> List[Dict[str, float]]:
        """Get trajectory as list of points
        
        Returns:
            List of trajectory points
        """
        return [
            {
                "timestamp": p.timestamp,
                "x": p.x,
                "y": p.y,
                "angle": math.degrees(p.angle),
            }
            for p in self.tracking_history
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_distance": self.total_distance,
            "total_time": self.total_time,
            "average_speed": self.average_speed,
            "max_speed": self.max_speed,
            "track_points": len(self.tracking_history),
        }
    
    def reset(self):
        """Reset tracker"""
        self.tracking_history.clear()
        self.total_distance = 0.0
        self.total_time = 0.0
        self.average_speed = 0.0
        self.max_speed = 0.0
        logger.info("Movement tracker reset")
    
    def export_data(self, filename: str):
        """Export tracking data to file
        
        Args:
            filename: Output filename
        """
        try:
            import json
            data = {
                "trajectory": self.get_trajectory(),
                "statistics": self.get_statistics(),
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Tracking data exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting tracking data: {e}")
