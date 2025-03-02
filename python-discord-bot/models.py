"""
Model definitions and configurations for LLM providers.
Contains available models and their default configurations.
"""

from typing import Dict, Any, List, Optional

# OpenAI Models
OPENAI_MODELS = {
    "gpt-4": {
        "name": "GPT-4",
        "description": "Most capable GPT-4 model, better at reasoning and complex tasks",
        "default_temperature": 0.7,
        "max_tokens": 4096,
        "supports_functions": True,
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "description": "Faster version of GPT-4 with improved capabilities",
        "default_temperature": 0.7,
        "max_tokens": 4096,
        "supports_functions": True,
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "Fast, economical model with good capabilities",
        "default_temperature": 0.7,
        "max_tokens": 4096,
        "supports_functions": True,
    }
}

# Anthropic Models
ANTHROPIC_MODELS = {
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "description": "Most powerful Claude model, best reasoning and complex task handling",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    },
    "claude-3-sonnet-20240229": {
        "name": "Claude 3 Sonnet",
        "description": "Balanced model for most tasks with good performance",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    },
    "claude-3-haiku-20240307": {
        "name": "Claude 3 Haiku",
        "description": "Fast, efficient model for simpler tasks",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    }
}

# Mistral Models
MISTRAL_MODELS = {
    "mistral-large-latest": {
        "name": "Mistral Large",
        "description": "Flagship Mistral model with advanced reasoning abilities",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    },
    "mistral-medium-latest": {
        "name": "Mistral Medium", 
        "description": "Well-balanced model for most use cases",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    },
    "mistral-small-latest": {
        "name": "Mistral Small",
        "description": "Faster, more efficient model for simpler tasks",
        "default_temperature": 0.7,
        "max_tokens": 4096,
    }
}

# Combined model list by provider
MODELS_BY_PROVIDER = {
    "openai": OPENAI_MODELS,
    "anthropic": ANTHROPIC_MODELS,
    "mistral": MISTRAL_MODELS
}

# Default models by provider
DEFAULT_MODELS = {
    "openai": "gpt-4-turbo",
    "anthropic": "claude-3-sonnet-20240229",
    "mistral": "mistral-medium-latest"
}

# Role-specific prompts
ROLE_PROMPTS = {
    "Principal Investigator": """You are a Principal Investigator with expertise in {expertise}.
Your goal is to {goal}.
Guide the research direction and ask high-level questions.
Synthesize ideas from the team and identify promising directions.
Set priorities and ensure the team stays focused on the most important aspects.
""",
    
    "Scientist": """You are a Scientist specializing in {expertise}.
Your goal is to {goal}.
Provide detailed technical insights on topics related to your expertise.
Analyze data and experimental approaches with precision.
Ask probing questions that advance the scientific understanding.
""",
    
    "Critic": """You are a Scientific Critic with expertise in {expertise}.
Your goal is to {goal}.
Identify potential flaws in reasoning, methodology, or conclusions.
Challenge assumptions constructively, without being dismissive.
Suggest improvements to strengthen the research.
Ensure the team maintains intellectual honesty and scientific integrity.
"""
}

# System prompts for different agent functions
SYSTEM_PROMPTS = {
    "brainstorming": """You are participating in a scientific brainstorming session with multiple AI research agents.
The topic is: {agenda}

Guidelines:
- Respond as {agent_name}, a {agent_role} with expertise in {expertise}
- Stay in character and maintain your specific perspective
- Be concise and focused in your contributions
- Build upon others' ideas when appropriate
- {rules}

This is round {current_round} of {total_rounds}.
""",
    
    "individual_meeting": """You are {agent_name}, a {agent_role} with expertise in {expertise}.
You are having a one-on-one meeting with a researcher.

Your goal is to {goal}

Guidelines:
- Provide detailed, thoughtful responses based on your expertise
- Answer questions thoroughly while staying concise
- Suggest new ideas or approaches when appropriate
- {rules}
""",
    
    "critic_review": """You are a Scientific Critic with expertise in critical analysis of research.
Review the following statement and provide constructive criticism:

Guidelines:
- Identify potential flaws in reasoning or methodology
- Suggest alternative interpretations or approaches
- Be constructive, not dismissive
- Keep your response concise and focused
"""
}

def get_model_info(provider: str, model_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about a specific model
    
    Args:
        provider: The model provider (openai, anthropic, mistral)
        model_id: The specific model ID (if None, returns default model info)
        
    Returns:
        Dictionary with model information
    """
    if provider not in MODELS_BY_PROVIDER:
        raise ValueError(f"Unknown provider: {provider}")
        
    provider_models = MODELS_BY_PROVIDER[provider]
    
    if model_id is None:
        model_id = DEFAULT_MODELS[provider]
        
    if model_id not in provider_models:
        raise ValueError(f"Unknown model: {model_id} for provider {provider}")
        
    return provider_models[model_id]

def get_role_prompt(role: str, expertise: str = "", goal: str = "") -> str:
    """
    Get a prompt template for a specific agent role
    
    Args:
        role: The agent role (Principal Investigator, Scientist, Critic)
        expertise: The agent's area of expertise
        goal: The agent's goal or objective
        
    Returns:
        Formatted prompt string
    """
    if role not in ROLE_PROMPTS:
        return f"You are an AI research assistant specializing in {expertise}. Your goal is to {goal}."
        
    return ROLE_PROMPTS[role].format(
        expertise=expertise or "scientific research",
        goal=goal or "provide insightful analysis and contribute to the research discussion"
    )

def get_system_prompt(
    prompt_type: str,
    agent_name: str = "",
    agent_role: str = "",
    expertise: str = "",
    goal: str = "",
    agenda: str = "",
    current_round: int = 1,
    total_rounds: int = 3,
    rules: str = ""
) -> str:
    """
    Get a system prompt for a specific interaction type
    
    Args:
        prompt_type: Type of system prompt (brainstorming, individual_meeting, critic_review)
        agent_name: Name of the agent
        agent_role: Role of the agent
        expertise: The agent's expertise
        goal: The agent's goal
        agenda: The discussion agenda
        current_round: Current round number
        total_rounds: Total number of rounds
        rules: Additional rules or constraints
        
    Returns:
        Formatted system prompt
    """
    if prompt_type not in SYSTEM_PROMPTS:
        return f"You are {agent_name}, an AI research assistant."
        
    return SYSTEM_PROMPTS[prompt_type].format(
        agent_name=agent_name,
        agent_role=agent_role,
        expertise=expertise or "scientific research",
        goal=goal or "contribute to the discussion",
        agenda=agenda,
        current_round=current_round,
        total_rounds=total_rounds,
        rules=rules or "Be concise and scientifically accurate"
    )

def get_system_prompt_for_role(role: str, agent_data: Dict[str, str]) -> str:
    """
    Generate a system prompt for an agent based on their role
    
    Args:
        role: The agent's role (Principal Investigator, Scientist, Critic)
        agent_data: Dictionary containing agent information (name, expertise, goal)
        
    Returns:
        Formatted system prompt for the agent
    """
    # Extract agent information
    name = agent_data.get("name", "AI Agent")
    expertise = agent_data.get("expertise", "scientific research")
    goal = agent_data.get("goal", "contribute to the discussion")
    
    # Get the appropriate prompt type based on the role
    if role == "Principal Investigator":
        prompt_type = "individual_meeting"
    elif role == "Critic":
        prompt_type = "critic_review"
    else:
        prompt_type = "individual_meeting"
    
    # Generate the system prompt
    return get_system_prompt(
        prompt_type=prompt_type,
        agent_name=name,
        agent_role=role,
        expertise=expertise,
        goal=goal
    )

def get_default_model_for_provider(provider: str) -> str:
    """
    Get the default model for a given provider
    
    Args:
        provider: The model provider (openai, anthropic, mistral)
        
    Returns:
        Default model string for the provider
    """
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["anthropic"]) 