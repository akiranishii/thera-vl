"""
Command module for the Discord bot.
This directory will contain command groups organized by functionality.
"""

# This ensures the commands directory is recognized as a Python package
# We'll import command modules here to make them available when importing the commands package

from . import session_commands
from . import agent_commands
from . import meeting_commands
from . import brainstorm_commands 