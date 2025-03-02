#!/usr/bin/env python3
"""
Example script demonstrating how to use the LLM client.
This can be run directly for testing LLM API connections.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the parent directory to the path to import the LLM client
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Load environment variables
load_dotenv('../../.env.local')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('llm_example')

# Import the LLM client and models after setting up the path
from llm_client import llm_client
from models import get_model_info, get_system_prompt
from config import Config

async def test_provider(provider: str):
    """Test a specific LLM provider"""
    
    # Get provider-specific API key
    api_key = getattr(Config, f"{provider.upper()}_API_KEY")
    if not api_key:
        print(f"⚠️ {provider.capitalize()} API key not configured. Skipping test.")
        return False
    
    # Get default model info
    try:
        model_info = get_model_info(provider)
        print(f"\n--- Testing {provider.capitalize()} ({model_info['name']}) ---")
    except Exception as e:
        print(f"Error getting model info for {provider}: {str(e)}")
        return False
    
    # Create a simple prompt
    prompt = "What are three interesting applications of AI in scientific research?"
    system_prompt = "You are a helpful research assistant. Keep your answer concise and to the point."
    
    try:
        print(f"Sending request to {provider}...")
        response = await llm_client.generate_text(
            provider=provider,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=300
        )
        
        print(f"\nResponse from {provider.capitalize()}:")
        print("------------------------")
        print(response["text"])
        print("------------------------")
        print(f"Model: {response['model']}")
        
        if "usage" in response:
            tokens = response["usage"]
            if isinstance(tokens, dict):
                if "total_tokens" in tokens:
                    print(f"Total tokens: {tokens['total_tokens']}")
                elif "input_tokens" in tokens and "output_tokens" in tokens:
                    print(f"Input tokens: {tokens['input_tokens']}")
                    print(f"Output tokens: {tokens['output_tokens']}")
        
        return True
    
    except Exception as e:
        print(f"Error testing {provider}: {str(e)}")
        return False

async def test_chat_conversation(provider: str):
    """Test a multi-turn conversation with a model"""
    
    # Skip if provider not configured
    api_key = getattr(Config, f"{provider.upper()}_API_KEY")
    if not api_key:
        print(f"⚠️ {provider.capitalize()} API key not configured. Skipping chat test.")
        return False
    
    print(f"\n--- Testing {provider.capitalize()} Chat Conversation ---")
    
    # Sample conversation
    messages = [
        {"role": "user", "content": "What is gene editing?"},
        {"role": "assistant", "content": "Gene editing is a type of genetic engineering where DNA is inserted, deleted, modified or replaced in the genome of a living organism. Unlike early genetic engineering techniques that randomly inserted genetic material into a host genome, genome editing targets the insertions to site-specific locations. The most widely used and well-known technique is CRISPR-Cas9."},
        {"role": "user", "content": "What are some ethical concerns with this technology?"}
    ]
    
    system_prompt = "You are a scientific expert. Provide balanced, nuanced responses about complex scientific topics."
    
    try:
        print(f"Sending chat request to {provider}...")
        response = await llm_client.generate_chat_response(
            provider=provider,
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=400
        )
        
        print(f"\nResponse from {provider.capitalize()}:")
        print("------------------------")
        print(response["text"])
        print("------------------------")
        
        return True
    
    except Exception as e:
        print(f"Error testing {provider} chat: {str(e)}")
        return False

async def test_all_providers():
    """Test all available LLM providers"""
    providers = ["openai", "anthropic", "mistral"]
    
    print("Starting LLM client tests...")
    
    for provider in providers:
        await test_provider(provider)
    
    # Test conversation with the first available provider
    for provider in providers:
        api_key = getattr(Config, f"{provider.upper()}_API_KEY")
        if api_key:
            await test_chat_conversation(provider)
            break
    
    # Close the client connection
    await llm_client.close()

async def test_system_prompts():
    """Test system prompt generation"""
    
    print("\n--- Testing System Prompt Generation ---")
    
    # Test brainstorming prompt
    brainstorm_prompt = get_system_prompt(
        prompt_type="brainstorming",
        agent_name="Biologist",
        agent_role="Scientist",
        expertise="Molecular Biology",
        agenda="New approaches to gene therapy",
        current_round=1,
        total_rounds=3
    )
    
    print("\nBrainstorming System Prompt:")
    print("------------------------")
    print(brainstorm_prompt)
    print("------------------------")
    
    # Test individual meeting prompt
    meeting_prompt = get_system_prompt(
        prompt_type="individual_meeting",
        agent_name="Principal Investigator",
        agent_role="Principal Investigator",
        expertise="Neuroscience",
        goal="Provide guidance on experimental design"
    )
    
    print("\nIndividual Meeting System Prompt:")
    print("------------------------")
    print(meeting_prompt)
    print("------------------------")

async def main():
    """Main entry point"""
    print("=== LLM Client Test Script ===")
    
    await test_all_providers()
    await test_system_prompts()
    
    print("\nTests completed!")

if __name__ == "__main__":
    # Create the examples directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.realpath(__file__)), exist_ok=True)
    
    # Run the main function
    asyncio.run(main()) 