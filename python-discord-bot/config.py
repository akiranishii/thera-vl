import os
import logging
from dotenv import load_dotenv
import yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
def load_environment():
    """Load environment variables from .env, .env.local and local_env.yml files"""
    logger.info("Loading environment variables")
    
    # First try loading from .env file
    load_dotenv()
    
    # Also try loading from .env.local file in the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_local_path = os.path.join(project_root, ".env.local")
    if os.path.exists(env_local_path):
        logger.info(f"Loading environment variables from {env_local_path}")
        load_dotenv(dotenv_path=env_local_path)
    
    # Then try loading from local_env.yml if it exists
    local_env_path = os.path.join(os.path.dirname(__file__), "local_env.yml")
    if os.path.exists(local_env_path):
        logger.info(f"Loading environment variables from {local_env_path}")
        with open(local_env_path, "r") as file:
            try:
                config = yaml.safe_load(file)
                if config and isinstance(config, dict):
                    for key, value in config.items():
                        if key not in os.environ:
                            os.environ[key] = str(value)
                            logger.debug(f"Loaded {key} from local_env.yml")
            except Exception as e:
                logger.error(f"Error loading local_env.yml: {e}")

# Load environment variables
load_environment()

# Discord configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables")
    raise ValueError("DISCORD_TOKEN is required but was not found in environment variables")

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
APPLICATION_ID = os.getenv("APPLICATION_ID")

# API URLs
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3000")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")

# Other configurations
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true" 