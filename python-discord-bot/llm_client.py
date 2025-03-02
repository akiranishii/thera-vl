"""
LLM client for interfacing with different language model providers.
Handles API calls to OpenAI, Anthropic, and Mistral.
"""

import os
import json
import logging
import asyncio
import httpx
from typing import Dict, List, Any, Optional, Union, Literal
from config import Config

logger = logging.getLogger('llm_client')

# Define model types
ModelProvider = Literal["openai", "anthropic", "mistral"]

class LLMClient:
    """Client for interacting with various LLM providers"""
    
    def __init__(self):
        # API keys from environment variables
        self.openai_api_key = Config.OPENAI_API_KEY
        self.anthropic_api_key = Config.ANTHROPIC_API_KEY
        self.mistral_api_key = Config.MISTRAL_API_KEY
        
        # Check if keys are available
        self._check_api_keys()
        
        # Set default values for parameters
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
        
        # Initialize HTTP client
        self.http_client = None
    
    def _check_api_keys(self):
        """Check if necessary API keys are available"""
        missing_keys = []
        
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
            logger.warning("OpenAI API key not found. OpenAI models will not be available.")
        
        if not self.anthropic_api_key:
            missing_keys.append("ANTHROPIC_API_KEY")
            logger.warning("Anthropic API key not found. Claude models will not be available.")
            
        if not self.mistral_api_key:
            missing_keys.append("MISTRAL_API_KEY")
            logger.warning("Mistral API key not found. Mistral models will not be available.")
        
        if missing_keys:
            logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
    
    async def _get_http_client(self):
        """Get or create an HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=60.0)
        return self.http_client
    
    async def close(self):
        """Close the HTTP client"""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
    
    async def generate_text(
        self,
        provider: ModelProvider,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the specified LLM provider
        
        Args:
            provider: The LLM provider to use ("openai", "anthropic", "mistral")
            prompt: The prompt or user message
            system_prompt: Optional system instructions for the model
            model: Model identifier (provider-specific)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Sequences that will stop generation
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Set defaults if not provided
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Select the appropriate provider
        if provider == "openai":
            return await self._generate_openai(
                prompt, system_prompt, model, temperature, max_tokens, stop_sequences, **kwargs
            )
        elif provider == "anthropic":
            return await self._generate_anthropic(
                prompt, system_prompt, model, temperature, max_tokens, stop_sequences, **kwargs
            )
        elif provider == "mistral":
            return await self._generate_mistral(
                prompt, system_prompt, model, temperature, max_tokens, stop_sequences, **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using OpenAI"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Default to GPT-4 if not specified
        model = model or "gpt-4"
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "n": 1,
            "stream": False,
        }
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "finish_reason": result["choices"][0]["finish_reason"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Anthropic Claude"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Default to Claude 3 Opus if not specified
        model = model or "claude-3-opus-20240229"
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if stop_sequences:
            payload["stop_sequences"] = stop_sequences
            
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["content"][0]["text"],
                "finish_reason": result.get("stop_reason", ""),
                "model": result["model"],
                "usage": {
                    "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                },
                "provider": "anthropic"
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def _generate_mistral(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Mistral AI"""
        if not self.mistral_api_key:
            raise ValueError("Mistral API key not configured")
        
        # Default to Mistral Medium if not specified
        model = model or "mistral-medium"
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.mistral_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "finish_reason": result["choices"][0]["finish_reason"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "provider": "mistral"
            }
            
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            raise
    
    async def generate_chat_response(
        self,
        provider: ModelProvider,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response based on a conversation history
        
        Args:
            provider: The LLM provider to use
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system instructions
            model: Model identifier (provider-specific)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing the response and metadata
        """
        if provider == "openai":
            return await self._generate_openai_chat(
                messages, system_prompt, model, temperature, max_tokens, **kwargs
            )
        elif provider == "anthropic":
            return await self._generate_anthropic_chat(
                messages, system_prompt, model, temperature, max_tokens, **kwargs
            )
        elif provider == "mistral":
            return await self._generate_mistral_chat(
                messages, system_prompt, model, temperature, max_tokens, **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _generate_openai_chat(
        self, 
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using OpenAI's chat API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Set defaults
        model = model or "gpt-4"
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Prepare the messages
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        # Add the conversation history
        for message in messages:
            # Ensure message has required fields
            if "role" not in message or "content" not in message:
                continue
                
            # Map roles if needed (assistant, user, system are standard)
            role = message["role"]
            if role not in ["assistant", "user", "system"]:
                role = "user"  # Default to user for unknown roles
                
            formatted_messages.append({
                "role": role,
                "content": message["content"]
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "n": 1,
            "stream": False,
        }
        
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "finish_reason": result["choices"][0]["finish_reason"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI chat API error: {str(e)}")
            raise
    
    async def _generate_anthropic_chat(
        self, 
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using Anthropic's chat API"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Set defaults
        model = model or "claude-3-opus-20240229"
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Format messages for Anthropic API
        formatted_messages = []
        for message in messages:
            # Ensure message has required fields
            if "role" not in message or "content" not in message:
                continue
                
            # Map roles to Anthropic's format
            role = message["role"]
            if role == "assistant":
                role = "assistant"
            else:
                role = "user"  # Default to user for all other roles
                
            formatted_messages.append({
                "role": role,
                "content": message["content"]
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["content"][0]["text"],
                "finish_reason": result.get("stop_reason", ""),
                "model": result["model"],
                "usage": {
                    "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                },
                "provider": "anthropic"
            }
            
        except Exception as e:
            logger.error(f"Anthropic chat API error: {str(e)}")
            raise
    
    async def _generate_mistral_chat(
        self, 
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response using Mistral's chat API"""
        if not self.mistral_api_key:
            raise ValueError("Mistral API key not configured")
        
        # Set defaults
        model = model or "mistral-medium"
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        # Format messages for Mistral API
        formatted_messages = []
        
        # Add system message if provided
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        for message in messages:
            # Ensure message has required fields
            if "role" not in message or "content" not in message:
                continue
                
            # Map roles to Mistral's format (system, user, assistant)
            role = message["role"]
            if role not in ["system", "user", "assistant"]:
                role = "user"  # Default to user for unknown roles
                
            formatted_messages.append({
                "role": role,
                "content": message["content"]
            })
        
        # Prepare request payload
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add additional kwargs
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            client = await self._get_http_client()
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.mistral_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "finish_reason": result["choices"][0]["finish_reason"],
                "model": result["model"],
                "usage": result.get("usage", {}),
                "provider": "mistral"
            }
            
        except Exception as e:
            logger.error(f"Mistral chat API error: {str(e)}")
            raise

# Create a singleton instance
llm_client = LLMClient() 