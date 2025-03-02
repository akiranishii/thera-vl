"""
Configuration settings for the Discord bot.
Includes default values and environment variable loading.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    """Configuration class for the Discord bot"""
    
    # Load environment variables the first time the class is imported
    load_dotenv(Path(__file__).parent.parent / '.env.local')
    
    # Discord configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = '/'
    
    # Database configuration
    DB_HOST = os.getenv('SUPABASE_URL')
    DB_PASSWORD = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # LLM API configuration - we'll support multiple providers
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    
    # Default LLM settings
    DEFAULT_LLM_PROVIDER = 'openai'  # Options: 'openai', 'anthropic', 'mistral'
    DEFAULT_OPENAI_MODEL = 'gpt-4'
    DEFAULT_ANTHROPIC_MODEL = 'claude-2'
    DEFAULT_MISTRAL_MODEL = 'mistral-large-latest'
    
    # System prompts
    DEFAULT_SYSTEM_PROMPT = "You are a helpful research and brainstorming assistant in Thera Virtual Lab."
    
    # App settings
    MAX_HISTORY_LENGTH = 10  # Maximum number of messages to keep in conversation history
    LOGGING_LEVEL = 'INFO'
    
    # Roles and permissions
    ADMIN_ROLE_NAME = 'Thera VL Admin'
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration values are present"""
        missing = []
        
        if not cls.DISCORD_TOKEN:
            missing.append('DISCORD_TOKEN')
        
        if not cls.DB_HOST or not cls.DB_PASSWORD:
            missing.append('Database credentials (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)')
        
        # At least one LLM provider is required
        if not any([cls.OPENAI_API_KEY, cls.ANTHROPIC_API_KEY, cls.MISTRAL_API_KEY]):
            missing.append('At least one LLM API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, or MISTRAL_API_KEY)')
        
        return missing 