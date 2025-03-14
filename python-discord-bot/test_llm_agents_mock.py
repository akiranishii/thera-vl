#!/usr/bin/env python

import asyncio
import logging
import os
import sys
import uuid
from typing import List, Dict, Optional
from unittest.mock import patch, MagicMock
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

# Add dotenv import at the top
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("llm_test")

# Log environment variable loading
logger.info(f"Loaded environment variables from {dotenv_path}")
logger.info(f"OpenAI API Key available: {bool(os.getenv('OPENAI_API_KEY'))}")
logger.info(f"Anthropic API Key available: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
logger.info(f"Mistral API Key available: {bool(os.getenv('MISTRAL_API_KEY'))}")

# Mock the required classes if the real ones aren't available
class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"

@dataclass
class LLMMessage:
    """A message in a conversation with an LLM."""
    role: str  # "system", "user", or "assistant"
    content: str
    name: Optional[str] = None  # For multi-agent conversations

@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, int]  # Token usage statistics

class ModelConfig:
    """Configuration for LLM models."""
    
    # OpenAI Models
    OPENAI_CHAT_MODEL = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Anthropic Models
    ANTHROPIC_CHAT_MODEL = "claude-3-opus-20240229"
    
    # Mistral Models
    MISTRAL_CHAT_MODEL = "mistral-large"
    
    # Default parameters
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2000
    
    # Role definitions
    SYSTEM_ROLE = "system"
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    
    # Agent roles
    PRINCIPAL_INVESTIGATOR_ROLE = "Principal Investigator"
    SCIENTIST_ROLE = "Scientist"
    CRITIC_ROLE = "Critic"
    
    # System prompts for different agent roles
    SYSTEM_PROMPTS = {
        PRINCIPAL_INVESTIGATOR_ROLE: """You are a Principal Investigator (PI) leading a research team.""",
        SCIENTIST_ROLE: """You are a research Scientist with specific expertise in {expertise}.""",
        CRITIC_ROLE: """You are a Critical Reviewer of scientific discussions."""
    }
    
    @classmethod
    def get_system_prompt(cls, role: str, expertise: Optional[str] = None) -> str:
        """Get the system prompt for a given role."""
        prompt = cls.SYSTEM_PROMPTS.get(role)
        if prompt and expertise and role == cls.SCIENTIST_ROLE:
            prompt = prompt.format(expertise=expertise)
        return prompt or "You are a helpful AI assistant."

# Mock LLMClient
class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self):
        """Initialize with mock data."""
        self.providers = {
            LLMProvider.OPENAI.value: {
                "is_available": True,
                "default_model": "gpt-4-turbo-preview"
            },
            LLMProvider.ANTHROPIC.value: {
                "is_available": True,
                "default_model": "claude-3-opus-20240229"
            },
            LLMProvider.MISTRAL.value: {
                "is_available": True,
                "default_model": "mistral-large"
            }
        }
        logger.info("Initialized Mock LLM Client")
    
    def get_available_providers(self):
        """Return mock available providers."""
        return self.providers
    
    async def generate_response(
        self,
        provider: LLMProvider,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a mock response."""
        # Get the user message to include in the response
        user_message = next((m.content for m in messages if m.role == "user"), "")
        
        # Create a mock response that references the user's query
        if provider == LLMProvider.OPENAI:
            content = f"[OpenAI Mock Response] LLMs are neural networks trained on vast text datasets to predict and generate human-like text. They utilize transformer architectures with self-attention mechanisms to process and understand context effectively."
            model_used = model or "gpt-4-turbo-preview"
            usage = {"prompt_tokens": 50, "completion_tokens": 40, "total_tokens": 90}
        
        elif provider == LLMProvider.ANTHROPIC:
            content = f"[Anthropic Mock Response] Large Language Models are neural networks that learn patterns from text data and generate responses based on statistical patterns they've identified. They excel at tasks requiring linguistic understanding."
            model_used = model or "claude-3-opus-20240229"
            usage = {"input_tokens": 55, "output_tokens": 45, "total_tokens": 100}
        
        elif provider == LLMProvider.MISTRAL:
            content = f"[Mistral Mock Response] LLMs function by analyzing patterns in language data and generating text based on learned probabilities. Their transformer architecture processes relationships between words to produce contextually relevant outputs."
            model_used = model or "mistral-large"
            usage = {"prompt_tokens": 45, "completion_tokens": 35, "total_tokens": 80}
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Simulate a slight delay to mimic API call
        await asyncio.sleep(0.5)
        
        return LLMResponse(
            content=content,
            provider=provider,
            model=model_used,
            usage=usage
        )

# Mock AgentOrchestrator
class MockAgentOrchestrator:
    """Mock Agent Orchestrator for testing."""
    
    def __init__(self, llm_client):
        """Initialize with the given LLM client."""
        self.llm_client = llm_client
        self.active_meetings = {}
        self.parallel_groups = {}
        logger.info("Initialized Mock Agent Orchestrator")
    
    async def initialize_meeting(self, meeting_id, session_id, agents, agenda, round_count, parallel_index=0):
        """Initialize a mock meeting."""
        logger.info(f"Initializing mock meeting {meeting_id}")
        self.active_meetings[meeting_id] = {
            "id": meeting_id,
            "session_id": session_id,
            "agents": agents,
            "agenda": agenda,
            "round_count": round_count,
            "current_round": 0,
            "is_completed": False,
            "thread": None,
            "parallel_index": parallel_index,
            "messages": [],
            "is_active": True,
            "summary": None
        }
        
        if session_id not in self.parallel_groups:
            self.parallel_groups[session_id] = set()
        self.parallel_groups[session_id].add(meeting_id)
        
        return True
    
    async def start_conversation(self, meeting_id, interaction, live_mode=True):
        """Start a mock conversation."""
        logger.info(f"Starting mock conversation for meeting {meeting_id} (live_mode: {live_mode})")
        
        meeting_data = self.active_meetings.get(meeting_id)
        if meeting_data:
            meeting_data["live_mode"] = live_mode
            
        return True
    
    async def end_conversation(self, meeting_id):
        """End a mock conversation."""
        logger.info(f"Ending mock conversation for meeting {meeting_id}")
        
        meeting_data = self.active_meetings.get(meeting_id)
        if meeting_data:
            meeting_data["is_completed"] = True
            meeting_data["is_active"] = False
            
        return True
    
    async def generate_combined_summary(self, meetings):
        """Generate a mock combined summary."""
        logger.info(f"Generating mock combined summary for {len(meetings)} meetings")
        
        # Extract the agenda and agent names
        agenda = meetings[0]['agenda'] if meetings and 'agenda' in meetings[0] else "Unknown topic"
        
        # Create a mock combined summary
        return f"""[Mock Combined Summary for "{agenda}"]

Common Themes:
1. The importance of interdisciplinary approaches
2. The need for both technological and social solutions
3. The value of evidence-based policy frameworks

Unique Insights:
1. From Run 1: Innovation in carbon capture technologies shows promising results
2. From Run 2: Community-based initiatives have higher adoption rates

Integrated Conclusions:
This synthesis identifies that successful climate change mitigation requires a combination of technological innovation and social engagement strategies. Key recommendations include developing policy frameworks that incentivize both research and community adoption.
"""

class LLMTester:
    """Test LLM providers and agent conversations with mocks."""
    
    def __init__(self):
        """Initialize the tester with mock components."""
        self.llm_client = MockLLMClient()
        self.orchestrator = MockAgentOrchestrator(self.llm_client)
        
    async def test_providers(self):
        """Test all available LLM providers using mock responses."""
        logger.info("===== TESTING LLM PROVIDERS (MOCK) =====")
        
        available_providers = self.llm_client.get_available_providers()
        logger.info(f"Available providers: {list(available_providers.keys())}")
        
        # Test message that works for all providers
        messages = [
            LLMMessage(role="system", content="You are a helpful AI assistant for a scientific research team."),
            LLMMessage(role="user", content="Explain how LLMs work in 2-3 sentences.")
        ]
        
        success = True
        
        # Test OpenAI
        if LLMProvider.OPENAI.value in available_providers:
            success = success and await self._test_provider(LLMProvider.OPENAI, messages)
        else:
            logger.warning("OpenAI provider not available. Skipping test.")
        
        # Test Anthropic
        if LLMProvider.ANTHROPIC.value in available_providers:
            success = success and await self._test_provider(LLMProvider.ANTHROPIC, messages)
        else:
            logger.warning("Anthropic provider not available. Skipping test.")
        
        # Test Mistral
        if LLMProvider.MISTRAL.value in available_providers:
            success = success and await self._test_provider(LLMProvider.MISTRAL, messages)
        else:
            logger.warning("Mistral provider not available. Skipping test.")
        
        return success
    
    async def _test_provider(self, provider: LLMProvider, messages: List[LLMMessage]) -> bool:
        """Test a specific LLM provider using mock responses."""
        logger.info(f"Testing {provider.value} provider...")
        try:
            response = await self.llm_client.generate_response(
                provider=provider,
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            
            logger.info(f"Response from {provider.value}:")
            logger.info(f"Content: {response.content}")
            logger.info(f"Model: {response.model}")
            logger.info(f"Usage: {response.usage}")
            return True
            
        except Exception as e:
            logger.error(f"Error testing {provider.value}: {e}")
            return False
    
    async def test_agent_discussion(self):
        """Test the agent discussion functionality using mocks."""
        logger.info("\n===== TESTING AGENT DISCUSSION (MOCK) =====")
        
        # Create a mock meeting setup
        meeting_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        # Create mock agents for the discussion
        agents = [
            {
                "id": str(uuid.uuid4()),
                "name": "Principal Investigator",
                "role": "Lead",
                "expertise": None,
                "goal": "Oversee experiment design and coordinate discussion",
                "model": "openai"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Scientist 1",
                "role": "Scientist",
                "expertise": "Theoretical Analysis",
                "goal": "Provide theoretical analysis insights",
                "model": "openai"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Critic",
                "role": "Critical Reviewer",
                "expertise": None,
                "goal": "Challenge assumptions and ensure scientific rigor",
                "model": "openai"
            }
        ]
        
        # Test topic
        agenda = "How can we use AI to improve scientific discovery processes?"
        
        # Initialize a test meeting in the orchestrator
        logger.info(f"Initializing test meeting with ID: {meeting_id}")
        await self.orchestrator.initialize_meeting(
            meeting_id=meeting_id,
            session_id=session_id,
            agents=agents,
            agenda=agenda,
            round_count=1,
            parallel_index=0
        )
        
        # Test the start_conversation method
        logger.info("Starting test conversation")
        mock_interaction = MockDiscordInteraction()
        await self.orchestrator.start_conversation(
            meeting_id=meeting_id,
            interaction=mock_interaction,
            live_mode=True
        )
        
        # Simulate message generation for each agent
        logger.info("Simulating agent responses")
        for agent in agents:
            agent_name = agent.get("name")
            agent_role = agent.get("role")
            agent_expertise = agent.get("expertise", "General")
            
            # Create system and user prompts for the agent
            system_prompt = ModelConfig.get_system_prompt(agent_role, agent_expertise)
            
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(
                    role="user", 
                    content=f"Topic for discussion: {agenda}\n\nProvide your initial thoughts as the {agent_name} on this topic. Keep your response concise (2-3 sentences)."
                )
            ]
            
            # Get response from the agent's assigned model
            try:
                provider = LLMProvider.OPENAI  # Default to OpenAI for testing
                
                response = await self.llm_client.generate_response(
                    provider=provider,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150
                )
                
                logger.info(f"Response from {agent_name} ({agent_role}):")
                logger.info(response.content)
                
            except Exception as e:
                logger.error(f"Error generating response for {agent_name}: {e}")
        
        # End the conversation
        logger.info("Ending test conversation")
        await self.orchestrator.end_conversation(meeting_id=meeting_id)
        
        logger.info("Agent discussion test completed")
        return True
        
    async def test_combined_summary(self):
        """Test the combined summary generation for parallel meetings."""
        logger.info("\n===== TESTING COMBINED SUMMARY (MOCK) =====")
        
        # Create mock meetings
        meetings = [
            {
                "id": str(uuid.uuid4()),
                "agenda": "How can we improve climate change mitigation strategies?",
                "agents": [
                    {"name": "Principal Investigator"},
                    {"name": "Scientist 1"},
                    {"name": "Critic"}
                ],
                "summary": "The team discussed various climate change mitigation strategies. Key points included carbon capture technologies, renewable energy transition, and policy frameworks."
            },
            {
                "id": str(uuid.uuid4()),
                "agenda": "How can we improve climate change mitigation strategies?",
                "agents": [
                    {"name": "Principal Investigator"},
                    {"name": "Scientist 1"},
                    {"name": "Critic"}
                ],
                "summary": "This discussion focused on behavioral and social aspects of climate change mitigation. The team highlighted the importance of public education and community-based initiatives."
            }
        ]
        
        try:
            # Generate a combined summary
            logger.info("Generating combined summary for parallel meetings")
            summary = await self.orchestrator.generate_combined_summary(meetings)
            
            logger.info("Combined Summary:")
            logger.info(summary)
            return True
            
        except Exception as e:
            logger.error(f"Error generating combined summary: {e}")
            return False

class MockDiscordInteraction:
    """Mock Discord interaction for testing."""
    def __init__(self):
        pass
        
    async def response_hook(self, *args, **kwargs):
        pass
    
    async def followup_hook(self, *args, **kwargs):
        pass

async def main():
    """Run all tests."""
    try:
        logger.info("Starting LLM and agent discussion mock tests")
        
        # Initialize tester
        tester = LLMTester()
        
        # Test all providers
        logger.info("\n")
        providers_success = await tester.test_providers()
        
        # Test agent discussion
        logger.info("\n")
        discussion_success = await tester.test_agent_discussion()
        
        # Test combined summary generation
        logger.info("\n")
        summary_success = await tester.test_combined_summary()
        
        # Print overall results
        logger.info("\n===== TEST RESULTS =====")
        logger.info(f"Provider Tests: {'PASSED' if providers_success else 'FAILED'}")
        logger.info(f"Agent Discussion Test: {'PASSED' if discussion_success else 'FAILED'}")
        logger.info(f"Combined Summary Test: {'PASSED' if summary_success else 'FAILED'}")
        
        return 0 if (providers_success and discussion_success and summary_success) else 1
        
    except Exception as e:
        logger.error(f"Error in test suite: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    """Run the test script."""
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 