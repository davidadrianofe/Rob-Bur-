#!/usr/bin/env python3
"""Movement Automation System with AI Guidance

Author: David Adriano Ferrari dos Santos
Description: Intelligent movement planning and execution with step-by-step automation
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import math
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MovementType(Enum):
    """Types of movement"""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    ROTATE = "rotate"
    STOP = "stop"
    IDLE = "idle"


@dataclass
class MovementStep:
    """Single movement step"""
    type: MovementType
    duration: float  # seconds
    power: float  # 0-100%
    angle: float = 0  # for rotation
    timestamp: float = 0.0
    completed: bool = False


@dataclass
class MovementSequence:
    """Sequence of movements"""
    name: str
    steps: List[MovementStep]
    total_distance: float = 0.0
    total_time: float = 0.0
    completed: bool = False


class MovementAutomation:
    """Intelligent movement automation with AI guidance"""

    def __init__(self, llm_engine):
        """Initialize movement automation
        
        Args:
            llm_engine: LLM engine for AI guidance
        """
        self.llm_engine = llm_engine
        self.current_position = {"x": 0.0, "y": 0.0, "angle": 0.0}
        self.velocity = {"linear": 0.0, "angular": 0.0}
        self.movement_history: List[MovementSequence] = []
        self.max_speed = 1.0  # m/s
        self.max_angular_velocity = 2.0  # rad/s
        self.wheel_radius = 0.05  # meters
        self.axle_length = 0.2  # meters
        
        logger.info("Movement Automation system initialized")

    def execute_movement(
        self,
        actions: List[Dict[str, Any]],
        ai_guidance: str = "",
    ) -> Dict[str, Any]:
        """Execute movement sequence with AI guidance
        
        Args:
            actions: List of action dictionaries
            ai_guidance: AI guidance text
            
        Returns:
            Movement result dictionary
        """
        logger.info(f"Executing {len(actions)} movement actions")
        logger.debug(f"AI Guidance: {ai_guidance}")
        
        sequence = MovementSequence(
            name=f"Movement_{time.time()}",
            steps=[],
        )
        
        total_distance = 0.0
        total_time = 0.0
        
        try:
            for action in actions:
                step = self._create_movement_step(action)
                sequence.steps.append(step)
                
                # Execute step
                result = self._execute_step(step)
                
                total_distance += result["distance"]
                total_time += result["time"]
                step.completed = True
                
                logger.info(
                    f"Executed: {step.type.value} "
                    f"(Distance: {result['distance']:.2f}m, Time: {result['time']:.2f}s)"
                )
            
            sequence.total_distance = total_distance
            sequence.total_time = total_time
            sequence.completed = True
            
            self.movement_history.append(sequence)
            
            return {
                "success": True,
                "distance": total_distance,
                "time": total_time,
                "position": self.current_position.copy(),
                "steps_executed": len(actions),
            }
        
        except Exception as e:
            logger.error(f"Error executing movement: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_distance": total_distance,
            }

    def _create_movement_step(self, action: Dict[str, Any]) -> MovementStep:
        """Create movement step from action
        
        Args:
            action: Action dictionary
            
        Returns:
            MovementStep object
        """
        action_type = action.get("type", "idle")
        duration = action.get("duration", 1.0)
        power = action.get("power", 100)
        angle = action.get("angle", 0)
        
        movement_type_map = {
            "move_forward": MovementType.FORWARD,
            "move_backward": MovementType.BACKWARD,
            "turn_left": MovementType.LEFT,
            "turn_right": MovementType.RIGHT,
            "rotate": MovementType.ROTATE,
            "stop": MovementType.STOP,
            "idle": MovementType.IDLE,
        }
        
        movement_type = movement_type_map.get(action_type, MovementType.IDLE)
        
        return MovementStep(
            type=movement_type,
            duration=duration,
            power=power,
            angle=angle,
            timestamp=time.time(),
        )

    def _execute_step(self, step: MovementStep) -> Dict[str, Any]:
        """Execute a single movement step
        
        Args:
            step: MovementStep to execute
            
        Returns:
            Result dictionary with distance and time
        """
        distance = 0.0
        
        if step.type == MovementType.FORWARD:
            speed = (step.power / 100) * self.max_speed
            distance = speed * step.duration
            self._update_position_forward(distance)
            logger.debug(f"Moving forward: {distance:.2f}m")
        
        elif step.type == MovementType.BACKWARD:
            speed = (step.power / 100) * self.max_speed
            distance = -speed * step.duration
            self._update_position_forward(distance)
            logger.debug(f"Moving backward: {-distance:.2f}m")
        
        elif step.type == MovementType.LEFT:
            angle = math.radians(90 if step.angle == 0 else step.angle)
            self.current_position["angle"] += angle
            logger.debug(f"Turning left: {math.degrees(angle):.0f}°")
        
        elif step.type == MovementType.RIGHT:
            angle = math.radians(-90 if step.angle == 0 else -step.angle)
            self.current_position["angle"] += angle
            logger.debug(f"Turning right: {math.degrees(-angle):.0f}°")
        
        elif step.type == MovementType.ROTATE:
            angle = math.radians(step.angle)
            self.current_position["angle"] += angle
            logger.debug(f"Rotating: {step.angle:.0f}°")
        
        elif step.type == MovementType.STOP:
            self.velocity["linear"] = 0.0
            self.velocity["angular"] = 0.0
            logger.debug("Stopping")
        
        else:  # IDLE
            logger.debug("Idle")
        
        return {
            "distance": abs(distance),
            "time": step.duration,
            "position": self.current_position.copy(),
        }

    def _update_position_forward(self, distance: float):
        """Update position when moving forward
        
        Args:
            distance: Distance to move (positive or negative)
        """
        angle = self.current_position["angle"]
        dx = distance * math.cos(angle)
        dy = distance * math.sin(angle)
        
        self.current_position["x"] += dx
        self.current_position["y"] += dy

    def plan_path(
        self,
        target_x: float,
        target_y: float,
    ) -> List[MovementStep]:
        """Plan path to target position using AI
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            Planned movement steps
        """
        current_x = self.current_position["x"]
        current_y = self.current_position["y"]
        
        # Calculate distance and angle to target
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        
        logger.info(f"Planning path to ({target_x:.2f}, {target_y:.2f})")
        logger.info(f"Distance: {distance:.2f}m, Angle: {math.degrees(target_angle):.1f}°")
        
        steps = []
        
        # Rotate to face target
        current_angle = self.current_position["angle"]
        angle_diff = target_angle - current_angle
        
        # Normalize angle to [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        if abs(angle_diff) > 0.01:  # Small threshold
            rotation_step = MovementStep(
                type=MovementType.ROTATE,
                duration=abs(angle_diff) / self.max_angular_velocity,
                power=100,
                angle=math.degrees(angle_diff),
            )
            steps.append(rotation_step)
        
        # Move forward to target
        if distance > 0.01:
            forward_step = MovementStep(
                type=MovementType.FORWARD,
                duration=distance / self.max_speed,
                power=100,
            )
            steps.append(forward_step)
        
        return steps

    def get_position(self) -> Dict[str, float]:
        """Get current position
        
        Returns:
            Position dictionary {x, y, angle}
        """
        return self.current_position.copy()

    def get_movement_history(self) -> List[Dict[str, Any]]:
        """Get movement history
        
        Returns:
            List of movement sequence dictionaries
        """
        return [
            {
                "name": seq.name,
                "total_distance": seq.total_distance,
                "total_time": seq.total_time,
                "steps": len(seq.steps),
                "completed": seq.completed,
            }
            for seq in self.movement_history
        ]

    def reset_position(self):
        """Reset position to origin"""
        self.current_position = {"x": 0.0, "y": 0.0, "angle": 0.0}
        self.velocity = {"linear": 0.0, "angular": 0.0}
        logger.info("Position reset to origin")
