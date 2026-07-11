#!/usr/bin/env python3
"""Main Robot Controller

Author: David Adriano Ferrari dos Santos
Description: Central controller for all robot operations using AI/LLM
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from .llm_engine import LLMEngine
from .movement_automation import MovementAutomation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobotState(Enum):
    """Robot operating states"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    EXECUTING_COMMAND = "executing_command"
    ERROR = "error"
    STOPPED = "stopped"


class RobotMode(Enum):
    """Robot operational modes"""
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"
    SEMI_AUTONOMOUS = "semi_autonomous"
    LEARNING = "learning"


@dataclass
class RobotStatus:
    """Current robot status"""
    state: RobotState
    mode: RobotMode
    battery_level: float
    temperature: float
    active_motors: int
    distance_traveled: float
    timestamp: str
    last_command: Optional[str] = None
    error_count: int = 0
    execution_time: float = 0.0


class RobotController:
    """Main robot controller with AI integration"""

    def __init__(
        self,
        llm_engine: Optional[LLMEngine] = None,
        name: str = "Rob-Bur-",
        config_path: Optional[str] = None,
    ):
        """Initialize Robot Controller
        
        Args:
            llm_engine: LLM engine instance
            name: Robot name
            config_path: Path to configuration file
        """
        self.name = name
        self.llm_engine = llm_engine or LLMEngine()
        self.movement_controller = MovementAutomation(self.llm_engine)
        
        self.state = RobotState.IDLE
        self.mode = RobotMode.AUTONOMOUS
        self.battery_level = 100.0
        self.temperature = 25.0
        self.distance_traveled = 0.0
        self.error_count = 0
        self.command_history: List[str] = []
        self.max_command_history = 100
        
        logger.info(f"🤖 {name} initialized successfully")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command using AI processing
        
        Args:
            command: Natural language command
            
        Returns:
            Command execution result
        """
        self.state = RobotState.EXECUTING_COMMAND
        self.command_history.append(command)
        
        if len(self.command_history) > self.max_command_history:
            self.command_history.pop(0)
        
        logger.info(f"Executing command: {command}")
        
        try:
            # Get AI interpretation of command
            context = self._build_command_context()
            response = self.llm_engine.generate(
                prompt=f"Interpret and execute: {command}",
                context=context,
            )
            
            # Parse AI response for actions
            actions = self._parse_ai_response(response.text)
            
            # Execute movement
            result = self.movement_controller.execute_movement(
                actions=actions,
                ai_guidance=response.text,
            )
            
            self.distance_traveled += result.get("distance", 0)
            self.state = RobotState.IDLE
            
            return {
                "success": True,
                "command": command,
                "ai_interpretation": response.text,
                "actions_executed": actions,
                "result": result,
                "confidence": response.confidence,
                "processing_time": response.processing_time,
            }
        except Exception as e:
            self.error_count += 1
            self.state = RobotState.ERROR
            logger.error(f"Error executing command: {e}")
            return {
                "success": False,
                "command": command,
                "error": str(e),
                "error_count": self.error_count,
            }

    def _build_command_context(self) -> Dict[str, Any]:
        """Build context for command execution
        
        Returns:
            Context dictionary
        """
        return {
            "robot_name": self.name,
            "current_mode": self.mode.value,
            "battery_level": f"{self.battery_level:.1f}%",
            "distance_traveled": f"{self.distance_traveled:.2f}m",
            "temperature": f"{self.temperature:.1f}°C",
            "recent_commands": self.command_history[-5:],
        }

    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into executable actions
        
        Args:
            response: AI generated response
            
        Returns:
            List of action dictionaries
        """
        actions = []
        
        # Simple parsing logic - can be enhanced
        response_lower = response.lower()
        
        if "forward" in response_lower or "advance" in response_lower:
            actions.append({"type": "move_forward", "duration": 1.0})
        if "backward" in response_lower or "reverse" in response_lower:
            actions.append({"type": "move_backward", "duration": 1.0})
        if "left" in response_lower:
            actions.append({"type": "turn_left", "angle": 90})
        if "right" in response_lower:
            actions.append({"type": "turn_right", "angle": 90})
        if "stop" in response_lower:
            actions.append({"type": "stop"})
        
        # If no actions detected, default to idle
        if not actions:
            actions.append({"type": "idle"})
        
        return actions

    def set_mode(self, mode: RobotMode):
        """Set robot operating mode
        
        Args:
            mode: Desired robot mode
        """
        self.mode = mode
        logger.info(f"Robot mode set to: {mode.value}")

    def get_status(self) -> RobotStatus:
        """Get current robot status
        
        Returns:
            RobotStatus object
        """
        return RobotStatus(
            state=self.state,
            mode=self.mode,
            battery_level=self.battery_level,
            temperature=self.temperature,
            active_motors=0,  # Would be updated by hardware layer
            distance_traveled=self.distance_traveled,
            timestamp=datetime.now().isoformat(),
            last_command=self.command_history[-1] if self.command_history else None,
            error_count=self.error_count,
        )

    def get_status_dict(self) -> Dict[str, Any]:
        """Get status as dictionary
        
        Returns:
            Dictionary with status information
        """
        status = self.get_status()
        return {
            "name": self.name,
            "state": status.state.value,
            "mode": status.mode.value,
            "battery_level": status.battery_level,
            "temperature": status.temperature,
            "distance_traveled": status.distance_traveled,
            "timestamp": status.timestamp,
            "last_command": status.last_command,
            "error_count": status.error_count,
        }

    def update_battery(self, level: float):
        """Update battery level
        
        Args:
            level: Battery level (0-100)
        """
        self.battery_level = max(0, min(100, level))
        if self.battery_level < 10:
            logger.warning("⚠️ Low battery level")

    def update_temperature(self, temp: float):
        """Update robot temperature
        
        Args:
            temp: Temperature in Celsius
        """
        self.temperature = temp
        if temp > 60:
            logger.error(f"🔥 High temperature: {temp}°C")
            self.state = RobotState.ERROR

    def reset(self):
        """Reset robot to initial state"""
        self.state = RobotState.IDLE
        self.battery_level = 100.0
        self.temperature = 25.0
        self.distance_traveled = 0.0
        self.error_count = 0
        self.command_history.clear()
        logger.info(f"🤖 {self.name} reset")

    def get_ai_stats(self) -> Dict[str, Any]:
        """Get AI engine statistics
        
        Returns:
            Statistics dictionary
        """
        return self.llm_engine.get_stats()

    def shutdown(self):
        """Shutdown robot"""
        self.state = RobotState.STOPPED
        logger.info(f"🤖 {self.name} shutdown")
