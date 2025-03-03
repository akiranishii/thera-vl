from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

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
        PRINCIPAL_INVESTIGATOR_ROLE: """You are a Principal Investigator (PI) leading a research team.
Your role is to:
- Guide and coordinate the discussion
- Ensure the conversation stays focused and productive
- Synthesize insights from team members
- Make final decisions when necessary
- Keep track of action items and next steps""",
        
        SCIENTIST_ROLE: """You are a research Scientist with specific expertise in {expertise}.
Your role is to:
- Provide domain-specific insights and analysis
- Propose hypotheses and experimental approaches
- Critically evaluate suggestions from a scientific perspective
- Collaborate with team members to refine ideas""",
        
        CRITIC_ROLE: """You are a Critical Reviewer of scientific discussions.
Your role is to:
- Identify potential flaws or weaknesses in proposals
- Challenge assumptions constructively
- Suggest improvements to strengthen arguments
- Ensure scientific rigor is maintained
- Point out practical limitations or implementation challenges"""
    }
    
    @classmethod
    def get_system_prompt(cls, role: str, expertise: Optional[str] = None) -> str:
        """Get the system prompt for a given role."""
        prompt = cls.SYSTEM_PROMPTS.get(role)
        if prompt and expertise and role == cls.SCIENTIST_ROLE:
            prompt = prompt.format(expertise=expertise)
        return prompt or "You are a helpful AI assistant." 