#!/usr/bin/env python3
"""
TheraLab Discord Bot Runner

This script starts the Discord bot with proper environment setup.
"""

import os
import sys
import logging
import argparse
import asyncio
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run")

def setup_environment():
    """Verify environment setup and dependencies before running the bot."""
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        env_example = Path(__file__).parent / ".env.example"
        if env_example.exists():
            logger.warning(f".env file not found. Creating from .env.example...")
            # Copy the example file
            with open(env_example, "r") as src, open(env_file, "w") as dest:
                dest.write(src.read())
            logger.warning(f"Created .env file. Please edit it and add your API keys.")
            logger.warning(f"Path: {env_file.absolute()}")
            return False
        else:
            logger.error(f".env file not found and .env.example is missing.")
            logger.error(f"Please create a .env file with your API keys.")
            return False
    
    # Check for empty API keys
    with open(env_file, "r") as f:
        env_content = f.read()
    
    empty_keys = []
    for key in ["DISCORD_BOT_TOKEN", "DISCORD_GUILD_ID"]:
        if f"{key}=" in env_content or f"{key}=your_" in env_content:
            empty_keys.append(key)
    
    if empty_keys:
        logger.error(f"The following keys are empty or unset in your .env file: {', '.join(empty_keys)}")
        logger.error(f"Please edit {env_file.absolute()} and add the missing values.")
        return False
    
    # Verify LLM providers
    llm_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MISTRAL_API_KEY"]
    available_llms = []
    
    for key in llm_keys:
        if key in env_content and not (f"{key}=" in env_content or f"{key}=your_" in env_content):
            available_llms.append(key.replace("_API_KEY", "").lower())
    
    if not available_llms:
        logger.warning("No LLM provider API keys found. Lab meeting features will be limited.")
        logger.warning(f"Consider adding at least one of: {', '.join(llm_keys)}")
    else:
        logger.info(f"Found API keys for these LLM providers: {', '.join(available_llms)}")
    
    # Check for required packages
    try:
        import dotenv
        import discord
        import yaml
        logger.info("All required packages are installed.")
    except ImportError as e:
        logger.error(f"Missing required package: {e}")
        logger.error("Please run: pip install -r requirements.txt")
        return False
    
    return True

def run_bot():
    """Run the Discord bot."""
    if not setup_environment():
        logger.error("Environment setup incomplete. Please fix the issues above.")
        if input("Continue anyway? (y/N): ").lower() != 'y':
            return 1
    
    logger.info("Starting Discord bot...")
    try:
        # Run the main script
        script_path = Path(__file__).parent / "main.py"
        return subprocess.call([sys.executable, str(script_path)])
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1

def run_tests(mock=True):
    """Run the test suite."""
    logger.info(f"Running {'mock' if mock else 'real'} tests...")
    try:
        # Run the test script
        script_name = "test_llm_agents_mock.py" if mock else "test_llm_agents.py"
        script_path = Path(__file__).parent / script_name
        return subprocess.call([sys.executable, str(script_path)])
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TheraLab Discord Bot Runner")
    
    # Add command line arguments
    parser.add_argument("--test", action="store_true", help="Run the test suite instead of the bot")
    parser.add_argument("--real-test", action="store_true", help="Run tests with real API calls (requires API keys)")
    parser.add_argument("--check-env", action="store_true", help="Only check environment setup without running the bot")
    
    args = parser.parse_args()
    
    if args.check_env:
        if setup_environment():
            logger.info("Environment setup looks good!")
            sys.exit(0)
        else:
            logger.error("Environment setup has issues that need to be fixed.")
            sys.exit(1)
    elif args.test:
        sys.exit(run_tests(mock=True))
    elif args.real_test:
        sys.exit(run_tests(mock=False))
    else:
        sys.exit(run_bot()) 