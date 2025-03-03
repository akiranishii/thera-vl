import os
import logging
import openai
import anthropic
from typing import List, Dict, Optional, Union
from models import LLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for making API calls to various LLM providers."""
    
    def __init__(self):
        """Initialize API clients for each provider."""
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize Anthropic client
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Initialize Mistral client (when available)
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        
        logger.info("Initialized LLM clients")

    async def generate_response(
        self,
        provider: LLMProvider,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response from the specified LLM provider.
        
        Args:
            provider: The LLM provider to use
            messages: List of messages in the conversation
            model: Specific model to use (optional)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in the response
            
        Returns:
            LLMResponse containing the generated text and metadata
        """
        try:
            if provider == LLMProvider.OPENAI:
                return await self._generate_openai_response(
                    messages=messages,
                    model=model or "gpt-4-turbo-preview",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic_response(
                    messages=messages,
                    model=model or "claude-3-opus-20240229",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == LLMProvider.MISTRAL:
                return await self._generate_mistral_response(
                    messages=messages,
                    model=model or "mistral-large",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error generating response from {provider}: {e}")
            raise

    async def _generate_openai_response(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> LLMResponse:
        """Generate a response using OpenAI's API."""
        try:
            # Convert our message format to OpenAI's format
            openai_messages = [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]
            
            # Make the API call
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_anthropic_response(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> LLMResponse:
        """Generate a response using Anthropic's API."""
        try:
            # Convert our messages to Anthropic's format
            # Note: Anthropic uses a different message format, so we need to adapt
            system_message = next((msg for msg in messages if msg.role == "system"), None)
            conversation = [msg for msg in messages if msg.role != "system"]
            
            # Create the messages array for Anthropic
            anthropic_messages = []
            if system_message:
                anthropic_messages.append({
                    "role": "assistant",
                    "content": system_message.content
                })
            
            for msg in conversation:
                anthropic_messages.append({
                    "role": "user" if msg.role == "user" else "assistant",
                    "content": msg.content
                })
            
            # Make the API call
            response = await self.anthropic_client.messages.create(
                model=model,
                messages=anthropic_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return LLMResponse(
                content=response.content[0].text,
                provider=LLMProvider.ANTHROPIC,
                model=model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def _generate_mistral_response(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> LLMResponse:
        """Generate a response using Mistral's API.
        
        Note: This is a placeholder implementation. Update when Mistral's API is available.
        """
        try:
            # Convert our message format to Mistral's format
            mistral_messages = [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]
            
            # TODO: Replace with actual Mistral API call when available
            # This is a placeholder implementation
            response = {
                "content": "Mistral API integration coming soon",
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            return LLMResponse(
                content=response["content"],
                provider=LLMProvider.MISTRAL,
                model=model,
                usage=response["usage"]
            )
            
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise

    async def get_embedding(
        self,
        text: str,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None
    ) -> List[float]:
        """Get embeddings for the given text.
        
        Args:
            text: The text to get embeddings for
            provider: The provider to use for embeddings
            model: Specific embedding model to use
            
        Returns:
            List of embedding values
        """
        try:
            if provider == LLMProvider.OPENAI:
                response = await self.openai_client.embeddings.create(
                    model=model or "text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            else:
                raise ValueError(f"Embeddings not supported for provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise

# Create a singleton instance of LLMClient
llm_client = LLMClient() 