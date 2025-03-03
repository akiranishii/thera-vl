import os
import sys
import time
import json
import requests
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_local_path = os.path.join(project_root, ".env.local")
if os.path.exists(env_local_path):
    logger.info(f"Loading environment variables from {env_local_path}")
    load_dotenv(dotenv_path=env_local_path)

# Get token and application ID
token = os.getenv("DISCORD_TOKEN")
app_id = os.getenv("APPLICATION_ID")

if not token or not app_id:
    logger.error("Missing DISCORD_TOKEN or APPLICATION_ID in environment variables")
    sys.exit(1)

def list_global_commands():
    """List all global commands for the application"""
    url = f"https://discord.com/api/v10/applications/{app_id}/commands"
    headers = {
        "Authorization": f"Bot {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        commands = response.json()
        if commands:
            logger.info(f"Found {len(commands)} global commands:")
            for cmd in commands:
                logger.info(f"- {cmd['name']} (ID: {cmd['id']})")
            return commands
        else:
            logger.info("No global commands found")
            return []
    else:
        logger.error(f"Failed to list commands: {response.status_code} {response.text}")
        return []

def delete_global_command(command_id):
    """Delete a global command by ID"""
    url = f"https://discord.com/api/v10/applications/{app_id}/commands/{command_id}"
    headers = {
        "Authorization": f"Bot {token}"
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        logger.info(f"Successfully deleted command {command_id}")
        return True
    elif response.status_code == 429:
        # Handle rate limiting
        try:
            data = response.json()
            retry_after = data.get('retry_after', 1)
            logger.warning(f"Rate limited. Waiting {retry_after} seconds before retrying...")
            time.sleep(retry_after + 0.5)  # Add a small buffer
            
            # Try again
            return delete_global_command(command_id)
        except json.JSONDecodeError:
            logger.error("Failed to parse rate limit response")
            time.sleep(5)  # Default wait
            return False
    else:
        logger.error(f"Failed to delete command {command_id}: {response.status_code} {response.text}")
        return False

def delete_all_global_commands():
    """Delete all global commands"""
    commands = list_global_commands()
    
    if not commands:
        return
    
    logger.info(f"Attempting to delete {len(commands)} global commands...")
    
    for cmd in commands:
        delete_global_command(cmd['id'])
        # Add a small delay between requests to avoid rate limiting
        time.sleep(1)
    
    # Verify deletion
    remaining = list_global_commands()
    if not remaining:
        logger.info("All global commands have been deleted")
    else:
        logger.warning(f"{len(remaining)} commands still remain")

if __name__ == "__main__":
    logger.info("Starting command deletion script")
    delete_all_global_commands() 