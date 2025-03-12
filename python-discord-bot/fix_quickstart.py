#!/usr/bin/env python
"""
Quickstart Fix Utility

This script ensures that the quickstart command can be properly imported by both names.
"""

import os
import sys
import logging
from importlib import import_module, reload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("fix_quickstart")

def main():
    """Fix quickstart command issues."""
    try:
        # First ensure our symbolic link is working
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        quickstart_command_path = os.path.join(commands_dir, "quickstart_command.py")
        quickstart_commands_path = os.path.join(commands_dir, "quickstart_commands.py")
        
        # Check if the symbolic link exists
        if not os.path.exists(quickstart_commands_path):
            logger.info("Creating symbolic link from quickstart_command.py to quickstart_commands.py")
            if os.name == 'nt':  # Windows
                # On Windows, symlinks require admin or developer mode
                import shutil
                shutil.copy2(quickstart_command_path, quickstart_commands_path)
                logger.info("Created a copy (Windows doesn't easily support symlinks)")
            else:  # Unix-like
                os.symlink("quickstart_command.py", quickstart_commands_path)
                logger.info("Created symbolic link")
        else:
            logger.info("Symbolic link already exists")
        
        # Try importing the module both ways
        logger.info("Testing command imports...")
        
        try:
            mod1 = import_module("commands.quickstart_command")
            logger.info("Successfully imported commands.quickstart_command")
            
            # Check if it has the expected class
            if hasattr(mod1, "QuickstartCommand"):
                logger.info("Found QuickstartCommand class in quickstart_command")
            else:
                logger.warning("QuickstartCommand class NOT found in quickstart_command!")
        except Exception as e:
            logger.error(f"Error importing commands.quickstart_command: {e}")
        
        try:
            # Make sure we get a fresh import
            if "commands.quickstart_commands" in sys.modules:
                reload(sys.modules["commands.quickstart_commands"])
            else:
                mod2 = import_module("commands.quickstart_commands")
            
            logger.info("Successfully imported commands.quickstart_commands")
            
            # Check if it has the expected class
            if hasattr(mod2, "QuickstartCommand"):
                logger.info("Found QuickstartCommand class in quickstart_commands")
            else:
                logger.warning("QuickstartCommand class NOT found in quickstart_commands!")
        except Exception as e:
            logger.error(f"Error importing commands.quickstart_commands: {e}")
        
        logger.info("Import tests completed")
        logger.info("---------------------")
        logger.info("Now start your bot normally and the '/quickstart' command should work.")
        logger.info("If it still doesn't work, try deleting and re-registering your bot's slash commands in the Discord Developer Portal.")
        
    except Exception as e:
        logger.error(f"Error fixing quickstart: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 