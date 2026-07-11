#!/usr/bin/env python3
"""Main Application Entry Point

Author: David Adriano Ferrari dos Santos
Description: Rob-Bur- Robot Automation System with Local LLM
"""

import logging
import sys
from typing import Optional
from pathlib import Path

from core.llm_engine import LLMEngine
from core.robot_controller import RobotController, RobotMode
from monitoring.movement_tracker import MovementTracker
from monitoring.performance_monitor import PerformanceMonitor
from ai.decision_maker import DecisionMaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RobSystem:
    """Main Rob-Bur- System"""
    
    def __init__(
        self,
        robot_name: str = "Rob-Bur-",
        llm_model: str = "llama2",
    ):
        """Initialize robot system
        
        Args:
            robot_name: Robot name
            llm_model: LLM model to use
        """
        logger.info(f"\n🤖 Initializing {robot_name} System...")
        logger.info(f"CEO & Creator: David Adriano Ferrari dos Santos")
        
        # Initialize LLM Engine
        self.llm_engine = LLMEngine(model=llm_model)
        
        # Initialize Robot Controller
        self.robot = RobotController(
            llm_engine=self.llm_engine,
            name=robot_name,
        )
        
        # Initialize Monitoring
        self.movement_tracker = MovementTracker()
        self.performance_monitor = PerformanceMonitor()
        self.decision_maker = DecisionMaker(self.llm_engine)
        
        logger.info("✓ System initialized successfully")
        logger.info("-" * 60)
    
    def demo_basic_commands(self):
        """Run demo with basic commands"""
        logger.info("\n📋 Running Basic Commands Demo...\n")
        
        commands = [
            "Move forward",
            "Turn right 90 degrees",
            "Move forward again",
            "Stop",
        ]
        
        for cmd in commands:
            logger.info(f"\n>>> Executing: {cmd}")
            result = self.robot.execute_command(cmd)
            
            if result["success"]:
                logger.info(f"✓ Success")
                logger.info(f"  Position: {self.robot.movement_controller.get_position()}")
            else:
                logger.error(f"✗ Failed: {result.get('error')}")
    
    def demo_ai_decision_making(self):
        """Run demo with AI decision making"""
        logger.info("\n🧠 Running AI Decision Making Demo...\n")
        
        situations = [
            "Robot detected obstacle ahead",
            "Battery level is at 20%",
            "Target location is 5 meters away",
        ]
        
        for situation in situations:
            logger.info(f"\n>>> Situation: {situation}")
            decision = self.decision_maker.make_decision(
                situation=situation,
                options=["Continue", "Stop", "Change course"],
            )
            logger.info(f"Decision: {decision['recommendation'][:100]}...")
    
    def demo_monitoring(self):
        """Run demo with monitoring"""
        logger.info("\n📊 Running Monitoring Demo...\n")
        
        # Simulate some robot activity
        self.movement_tracker.add_track_point(
            timestamp=0.0,
            x=0.0,
            y=0.0,
            angle=0.0,
        )
        
        self.movement_tracker.add_track_point(
            timestamp=1.0,
            x=1.0,
            y=0.0,
            angle=0.0,
            velocity_linear=1.0,
        )
        
        self.movement_tracker.add_track_point(
            timestamp=2.0,
            x=1.0,
            y=1.0,
            angle=1.57,
            velocity_linear=1.0,
        )
        
        # Get statistics
        stats = self.movement_tracker.get_statistics()
        logger.info(f"\nTracking Statistics:")
        logger.info(f"  Total Distance: {stats['total_distance']:.2f}m")
        logger.info(f"  Total Time: {stats['total_time']:.2f}s")
        logger.info(f"  Average Speed: {stats['average_speed']:.2f}m/s")
        
        # Update performance metrics
        self.performance_monitor.update_cpu_usage(45.5)
        self.performance_monitor.update_memory_usage(60.0)
        self.performance_monitor.record_command_time("move_forward", 0.3)
        
        diagnostics = self.performance_monitor.get_diagnostics()
        logger.info(f"\nSystem Diagnostics:")
        logger.info(f"  Status: {diagnostics['status']}")
        logger.info(f"  Health Score: {diagnostics['health_score']:.1f}/100")
        logger.info(f"  CPU Usage: {diagnostics['metrics']['cpu_usage']:.1f}%")
        logger.info(f"  Memory Usage: {diagnostics['metrics']['memory_usage']:.1f}%")
    
    def print_status(self):
        """Print system status"""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 ROBOT STATUS")
        logger.info("=" * 60)
        
        status = self.robot.get_status_dict()
        logger.info(f"Name: {status['name']}")
        logger.info(f"State: {status['state']}")
        logger.info(f"Mode: {status['mode']}")
        logger.info(f"Battery: {status['battery_level']:.1f}%")
        logger.info(f"Temperature: {status['temperature']:.1f}°C")
        logger.info(f"Distance Traveled: {status['distance_traveled']:.2f}m")
        logger.info(f"Errors: {status['error_count']}")
        
        logger.info("\n" + "=" * 60)
        logger.info("💡 AI ENGINE")
        logger.info("=" * 60)
        
        ai_stats = self.robot.get_ai_stats()
        logger.info(f"Model: {ai_stats['model']}")
        logger.info(f"Cache Size: {ai_stats['cache_size']}")
        logger.info(f"Context Window: {ai_stats['context_window_size']}")
        logger.info(f"Temperature: {ai_stats['temperature']}")
    
    def interactive_mode(self):
        """Enter interactive mode"""
        logger.info("\n" + "=" * 60)
        logger.info("🎮 INTERACTIVE MODE")
        logger.info("=" * 60)
        logger.info("Enter commands to control the robot")
        logger.info("Type 'help' for available commands")
        logger.info("Type 'exit' to quit")
        logger.info("=" * 60 + "\n")
        
        while True:
            try:
                command = input(">>> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == "exit":
                    logger.info("Shutting down...")
                    break
                
                if command.lower() == "help":
                    logger.info("Available commands:")
                    logger.info("  move forward/backward")
                    logger.info("  turn left/right")
                    logger.info("  status")
                    logger.info("  battery <level>")
                    logger.info("  temp <celsius>")
                    logger.info("  reset")
                    logger.info("  help")
                    logger.info("  exit")
                    continue
                
                if command.lower() == "status":
                    self.print_status()
                    continue
                
                if command.lower().startswith("battery"):
                    try:
                        level = float(command.split()[1])
                        self.robot.update_battery(level)
                        logger.info(f"Battery set to {level}%")
                    except:
                        logger.error("Usage: battery <level>")
                    continue
                
                if command.lower().startswith("temp"):
                    try:
                        temp = float(command.split()[1])
                        self.robot.update_temperature(temp)
                        logger.info(f"Temperature set to {temp}°C")
                    except:
                        logger.error("Usage: temp <celsius>")
                    continue
                
                if command.lower() == "reset":
                    self.robot.reset()
                    logger.info("Robot reset")
                    continue
                
                # Execute as natural language command
                result = self.robot.execute_command(command)
                if result["success"]:
                    logger.info(f"✓ Command executed")
                    logger.info(f"  AI Interpretation: {result['ai_interpretation'][:100]}...")
                else:
                    logger.error(f"✗ Command failed: {result.get('error')}")
            
            except KeyboardInterrupt:
                logger.info("\nInterrupted by user")
                break
            except Exception as e:
                logger.error(f"Error: {e}")


def main():
    """Main entry point"""
    try:
        # Initialize system
        system = RobSystem(
            robot_name="Rob-Bur-",
            llm_model="llama2",
        )
        
        # Run demos
        system.demo_basic_commands()
        system.demo_ai_decision_making()
        system.demo_monitoring()
        
        # Print status
        system.print_status()
        
        # Enter interactive mode
        system.interactive_mode()
        
    except KeyboardInterrupt:
        logger.info("\nShutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
