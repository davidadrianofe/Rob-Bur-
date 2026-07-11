#!/usr/bin/env python3
"""Performance Monitoring System

Author: David Adriano Ferrari dos Santos
Description: Monitors and analyzes robot system performance
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors system performance with AI analytics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "response_time": 0.0,
            "command_count": 0,
            "error_count": 0,
            "uptime": 0.0,
        }
        self.start_time = time.time()
        self.command_times: list = []
        self.error_history: list = []
        
        logger.info("Performance monitor initialized")
    
    def update_cpu_usage(self, usage: float):
        """Update CPU usage
        
        Args:
            usage: CPU usage percentage (0-100)
        """
        self.metrics["cpu_usage"] = max(0, min(100, usage))
    
    def update_memory_usage(self, usage: float):
        """Update memory usage
        
        Args:
            usage: Memory usage percentage (0-100)
        """
        self.metrics["memory_usage"] = max(0, min(100, usage))
    
    def record_command_time(self, command: str, duration: float):
        """Record command execution time
        
        Args:
            command: Command name
            duration: Execution time in seconds
        """
        self.command_times.append({
            "command": command,
            "duration": duration,
            "timestamp": time.time(),
        })
        
        # Keep only recent 100 commands
        if len(self.command_times) > 100:
            self.command_times.pop(0)
        
        self.metrics["command_count"] += 1
        
        # Update average response time
        if len(self.command_times) > 0:
            avg_time = sum(c["duration"] for c in self.command_times) / len(self.command_times)
            self.metrics["response_time"] = avg_time
    
    def record_error(self, error_msg: str, error_type: str = "unknown"):
        """Record system error
        
        Args:
            error_msg: Error message
            error_type: Type of error
        """
        self.error_history.append({
            "message": error_msg,
            "type": error_type,
            "timestamp": time.time(),
        })
        
        # Keep only recent 50 errors
        if len(self.error_history) > 50:
            self.error_history.pop(0)
        
        self.metrics["error_count"] += 1
        logger.error(f"[{error_type}] {error_msg}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics
        
        Returns:
            Metrics dictionary
        """
        self.metrics["uptime"] = time.time() - self.start_time
        return self.metrics.copy()
    
    def get_health_score(self) -> float:
        """Calculate system health score (0-100)
        
        Returns:
            Health score
        """
        score = 100.0
        
        # Reduce score based on CPU usage
        if self.metrics["cpu_usage"] > 80:
            score -= 20
        elif self.metrics["cpu_usage"] > 60:
            score -= 10
        
        # Reduce score based on memory usage
        if self.metrics["memory_usage"] > 80:
            score -= 20
        elif self.metrics["memory_usage"] > 60:
            score -= 10
        
        # Reduce score based on errors
        if self.metrics["error_count"] > 10:
            score -= 30
        elif self.metrics["error_count"] > 5:
            score -= 15
        
        # Reduce score based on response time
        if self.metrics["response_time"] > 1.0:
            score -= 15
        elif self.metrics["response_time"] > 0.5:
            score -= 5
        
        return max(0, min(100, score))
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get system diagnostics
        
        Returns:
            Diagnostics dictionary
        """
        health_score = self.get_health_score()
        
        status = "OK"
        if health_score < 50:
            status = "CRITICAL"
        elif health_score < 70:
            status = "WARNING"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "health_score": health_score,
            "metrics": self.get_metrics(),
            "recent_errors": self.error_history[-5:],
            "recent_commands": self.command_times[-5:],
        }
