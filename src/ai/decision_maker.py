#!/usr/bin/env python3
"""AI Decision Making System

Author: David Adriano Ferrari dos Santos
Description: Intelligent decision-making using LLM and reinforcement learning
"""

import logging
from typing import Dict, Any, List, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionMaker:
    """AI-based decision maker for robot control"""
    
    def __init__(self, llm_engine):
        """Initialize decision maker
        
        Args:
            llm_engine: LLM engine for decision making
        """
        self.llm_engine = llm_engine
        self.decision_history: List[Dict[str, Any]] = []
        self.decision_outcomes: Dict[str, List[float]] = {}
        
        logger.info("Decision maker initialized")
    
    def make_decision(
        self,
        situation: str,
        context: Optional[Dict[str, Any]] = None,
        options: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Make decision based on situation and context
        
        Args:
            situation: Description of current situation
            context: Additional context information
            options: List of available options
            
        Returns:
            Decision dictionary with recommended action
        """
        # Build decision prompt
        prompt = f"""Make a decision for robot control:

Situation: {situation}
"""
        
        if options:
            prompt += f"\nAvailable options:\n"
            for i, option in enumerate(options, 1):
                prompt += f"{i}. {option}\n"
        
        prompt += "\nProvide your decision with reasoning."
        
        # Get AI response
        response = self.llm_engine.generate(
            prompt=prompt,
            context=context,
        )
        
        # Parse decision
        decision = {
            "situation": situation,
            "recommendation": response.text,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "processing_time": response.processing_time,
        }
        
        self.decision_history.append(decision)
        
        logger.info(
            f"Decision made (confidence: {response.confidence:.2f}): "
            f"{response.text[:50]}..."
        )
        
        return decision
    
    def evaluate_outcome(
        self,
        decision_id: int,
        outcome: str,
        success_rating: float,
    ):
        """Evaluate outcome of a decision
        
        Args:
            decision_id: ID of the decision
            outcome: Description of outcome
            success_rating: Success rating (0-1)
        """
        if decision_id < len(self.decision_history):
            decision = self.decision_history[decision_id]
            
            # Track decision outcomes
            rec = decision["recommendation"][:30]  # Use first 30 chars as key
            if rec not in self.decision_outcomes:
                self.decision_outcomes[rec] = []
            self.decision_outcomes[rec].append(success_rating)
            
            logger.info(
                f"Outcome recorded for decision {decision_id}: "
                f"success_rating={success_rating:.2f}"
            )
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get decision history
        
        Returns:
            List of decisions
        """
        return self.decision_history.copy()
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision statistics
        
        Returns:
            Statistics dictionary
        """
        avg_confidence = 0.0
        if self.decision_history:
            avg_confidence = sum(
                d["confidence"] for d in self.decision_history
            ) / len(self.decision_history)
        
        avg_outcomes = {}
        for decision, ratings in self.decision_outcomes.items():
            if ratings:
                avg_outcomes[decision] = sum(ratings) / len(ratings)
        
        return {
            "total_decisions": len(self.decision_history),
            "average_confidence": avg_confidence,
            "decision_outcomes": avg_outcomes,
        }
