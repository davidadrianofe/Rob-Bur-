#!/usr/bin/env python3
"""Motor Control System

Author: David Adriano Ferrari dos Santos
Description: Controls robot motors with PWM signals
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MotorType(Enum):
    """Motor types"""
    DC = "dc"
    SERVO = "servo"
    STEPPER = "stepper"


class Motor:
    """Represents a single motor"""
    
    def __init__(
        self,
        motor_id: int,
        motor_type: MotorType,
        pin_forward: int,
        pin_backward: int,
        pin_pwm: int,
    ):
        """Initialize motor
        
        Args:
            motor_id: Motor identifier
            motor_type: Type of motor
            pin_forward: Forward control pin
            pin_backward: Backward control pin
            pin_pwm: PWM pin
        """
        self.motor_id = motor_id
        self.motor_type = motor_type
        self.pin_forward = pin_forward
        self.pin_backward = pin_backward
        self.pin_pwm = pin_pwm
        self.power = 0  # 0-100%
        self.direction = 1  # 1 for forward, -1 for backward
        self.rpm = 0
        
        logger.info(
            f"Motor {motor_id} ({motor_type.value}) initialized on "
            f"pins F:{pin_forward} B:{pin_backward} PWM:{pin_pwm}"
        )
    
    def set_power(self, power: int, direction: int = 1):
        """Set motor power and direction
        
        Args:
            power: Power level (0-100)
            direction: Direction (1 for forward, -1 for backward)
        """
        self.power = max(0, min(100, power))
        self.direction = direction
        self.rpm = (self.power / 100) * 100  # Assuming max 100 RPM
        
        logger.debug(
            f"Motor {self.motor_id}: Power={self.power}% Direction={direction}"
        )
    
    def stop(self):
        """Stop motor"""
        self.power = 0
        self.rpm = 0
        logger.debug(f"Motor {self.motor_id} stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get motor status
        
        Returns:
            Status dictionary
        """
        return {
            "motor_id": self.motor_id,
            "type": self.motor_type.value,
            "power": self.power,
            "direction": self.direction,
            "rpm": self.rpm,
        }


class MotorController:
    """Controls multiple motors"""
    
    def __init__(self):
        """Initialize motor controller"""
        self.motors: Dict[int, Motor] = {}
        logger.info("Motor controller initialized")
    
    def add_motor(
        self,
        motor_id: int,
        motor_type: MotorType,
        pin_forward: int,
        pin_backward: int,
        pin_pwm: int,
    ) -> Motor:
        """Add motor to controller
        
        Args:
            motor_id: Motor identifier
            motor_type: Type of motor
            pin_forward: Forward control pin
            pin_backward: Backward control pin
            pin_pwm: PWM pin
            
        Returns:
            Motor object
        """
        motor = Motor(
            motor_id=motor_id,
            motor_type=motor_type,
            pin_forward=pin_forward,
            pin_backward=pin_backward,
            pin_pwm=pin_pwm,
        )
        self.motors[motor_id] = motor
        return motor
    
    def set_motor_power(self, motor_id: int, power: int, direction: int = 1):
        """Set power for specific motor
        
        Args:
            motor_id: Motor identifier
            power: Power level (0-100)
            direction: Direction (1 or -1)
        """
        if motor_id in self.motors:
            self.motors[motor_id].set_power(power, direction)
    
    def stop_motor(self, motor_id: int):
        """Stop specific motor
        
        Args:
            motor_id: Motor identifier
        """
        if motor_id in self.motors:
            self.motors[motor_id].stop()
    
    def stop_all(self):
        """Stop all motors"""
        for motor in self.motors.values():
            motor.stop()
        logger.info("All motors stopped")
    
    def get_status(self) -> Dict[int, Dict[str, Any]]:
        """Get status of all motors
        
        Returns:
            Dictionary of motor statuses
        """
        return {mid: motor.get_status() for mid, motor in self.motors.items()}
