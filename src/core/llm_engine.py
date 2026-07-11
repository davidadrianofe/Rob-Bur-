#!/usr/bin/env python3
"""Local LLM Engine for Robot Intelligence

Author: David Adriano Ferrari dos Santos
Description: Manages local LLM (Large Language Model) for robot decision making
"""

import requests
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM engine"""
    text: str
    confidence: float
    tokens_used: int
    processing_time: float
    reasoning: str


class LLMEngine:
    """Local LLM Engine for intelligent robot control"""

    def __init__(
        self,
        model: str = "llama2",
        ollama_host: str = "http://localhost:11434",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
    ):
        """Initialize LLM Engine
        
        Args:
            model: LLM model name (llama2, mistral, etc)
            ollama_host: Ollama server URL
            temperature: Model temperature (0.0-1.0)
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.ollama_host = ollama_host
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.api_endpoint = f"{ollama_host}/api/generate"
        self.context_window = []
        self.max_context_history = 10
        self.response_cache = {}
        
        logger.info(f"Initializing LLM Engine with model: {model}")
        self._check_connection()

    def _check_connection(self) -> bool:
        """Check connection to Ollama server"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Connected to Ollama server")
                return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to Ollama: {e}")
            logger.warning("Make sure Ollama is running: ollama serve")
            return False

    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> LLMResponse:
        """Generate response from LLM
        
        Args:
            prompt: Input prompt for the model
            context: Additional context for the model
            use_cache: Use cached responses if available
            
        Returns:
            LLMResponse with generated text and metadata
        """
        # Check cache
        cache_key = f"{prompt}_{json.dumps(context or {})}"
        if use_cache and cache_key in self.response_cache:
            return self.response_cache[cache_key]

        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

        try:
            start_time = time.time()
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "num_predict": self.max_tokens,
                    "stream": False,
                },
                timeout=30,
            )
            processing_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("response", "").strip()
                
                # Extract confidence and reasoning
                confidence = self._calculate_confidence(generated_text)
                reasoning = self._extract_reasoning(generated_text)
                tokens_used = data.get("eval_count", 0)

                result = LLMResponse(
                    text=generated_text,
                    confidence=confidence,
                    tokens_used=tokens_used,
                    processing_time=processing_time,
                    reasoning=reasoning,
                )

                # Update context window
                self._update_context_window(prompt, generated_text)
                
                # Cache result
                self.response_cache[cache_key] = result

                logger.info(
                    f"Generated response (confidence: {confidence:.2f}, "
                    f"time: {processing_time:.2f}s)"
                )
                return result
            else:
                logger.error(f"LLM API error: {response.status_code}")
                raise Exception(f"LLM API returned {response.status_code}")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt with context
        
        Args:
            context: Context information for the model
            
        Returns:
            System prompt string
        """
        base_prompt = (
            "You are an intelligent robot control system (Rob-Bur-) powered by AI. "
            "You make decisions about movement, automation, and monitoring. "
            "Be precise, efficient, and safety-conscious. "
            "Respond with clear actions and reasoning."
        )

        if context:
            base_prompt += f"\n\nCurrent Context:\n"
            for key, value in context.items():
                base_prompt += f"- {key}: {value}\n"

        # Add recent context from history
        if self.context_window:
            base_prompt += "\n\nRecent Interactions:\n"
            for item in self.context_window[-3:]:  # Last 3 interactions
                base_prompt += f"- {item}\n"

        return base_prompt

    def _update_context_window(self, prompt: str, response: str):
        """Update context window with new interaction
        
        Args:
            prompt: User prompt
            response: Model response
        """
        self.context_window.append(f"Q: {prompt} -> A: {response[:100]}...")
        if len(self.context_window) > self.max_context_history:
            self.context_window.pop(0)

    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score for response
        
        Args:
            response: Generated response
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple heuristic: longer, more detailed responses = higher confidence
        word_count = len(response.split())
        confidence = min(1.0, word_count / 50)  # 50 words = high confidence
        
        # Boost confidence if response contains reasoning markers
        if any(marker in response.lower() for marker in ["because", "therefore", "so"]):
            confidence = min(1.0, confidence + 0.1)
        
        return confidence

    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from response
        
        Args:
            response: Generated response
            
        Returns:
            Reasoning string
        """
        sentences = response.split(".")
        if len(sentences) > 1:
            return sentences[0].strip()
        return response[:100]

    def embed(self, text: str) -> List[float]:
        """Generate embeddings for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = requests.post(
                f"{self.ollama_host}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=10,
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
        return []

    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("LLM response cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get LLM engine statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "model": self.model,
            "cache_size": len(self.response_cache),
            "context_window_size": len(self.context_window),
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
