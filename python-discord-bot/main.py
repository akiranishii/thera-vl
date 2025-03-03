import os
import sys
import logging
import asyncio
import discord
from discord.ext import commands
import traceback
from typing import List, Optional

# Import configuration
from config import DISCORD_TOKEN, COMMAND_PREFIX, APPLICATION_ID, DEBUG_MODE

# Set up logging
logger = logging.getLogger(__name__)

# Initialize intents
intents = discord.Intents.default()
intents.message_content = True  # Need message content for processing messages
intents.members = True  # Need members for user lookups

# Create bot instance
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    application_id=APPLICATION_ID,
    help_command=commands.DefaultHelpCommand(
        no_category="Commands"
    )
)

# Extension/cog settings
INITIAL_EXTENSIONS = [
    "commands.lab_session_commands",
    "commands.lab_agent_commands",
    "commands.lab_meeting_commands",
    "commands.lab_transcript_commands",
    "commands.session_commands",
    "commands.quickstart_command",
    "commands.help_command"
]

# Event Handlers
@bot.event
async def on_ready():
    """Called when the bot is connected and ready."""
    logger.info(f"{bot.user.name} is connected to Discord!")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Connected to {len(bot.guilds)} guilds")
    
    # Get available LLM providers
    try:
        from llm_client import LLMClient
        llm_client = LLMClient()
        for provider_name, provider in llm_client.providers.items():
            logger.info(f"LLM Provider: {provider_name} - Available: {provider.is_available} - Default model: {provider.default_model}")
    except Exception as e:
        logger.error(f"Error loading LLM providers: {e}")
    
    # List all commands that were registered before syncing
    logger.info("=== COMMAND REGISTRATION STATUS ===")
    command_count = 0
    try:
        logger.info("Commands registered before syncing:")
        for cmd in bot.tree.get_commands():
            command_count += 1
            if isinstance(cmd, discord.app_commands.Group):
                logger.info(f"Command group: {cmd.name}")
                for subcmd in cmd.commands:
                    if isinstance(subcmd, discord.app_commands.Group):
                        logger.info(f"  Subgroup: {subcmd.name}")
                        for subsubcmd in subcmd.commands:
                            logger.info(f"    Subcommand: {subsubcmd.name}")
                    else:
                        logger.info(f"  Subcommand: {subcmd.name}")
            else:
                logger.info(f"Command: {cmd.name}")
    except Exception as e:
        logger.error(f"Error listing commands: {e}")
    
    if command_count == 0:
        logger.warning("No commands were registered! Check your extensions and command registration.")
    
    # Sync commands with Discord
    try:
        logger.info("Syncing commands with Discord...")
        
        # Sync all commands globally
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} commands globally")
        
        # List the final command tree
        cmds = []
        for cmd in bot.tree.get_commands():
            if isinstance(cmd, discord.app_commands.Group):
                for subcmd in cmd.commands:
                    if isinstance(subcmd, discord.app_commands.Group):
                        for subsubcmd in subcmd.commands:
                            cmds.append(f"{cmd.name} {subcmd.name} {subsubcmd.name}")
                    else:
                        cmds.append(f"{cmd.name} {subcmd.name}")
            else:
                cmds.append(cmd.name)
        
        if cmds:
            logger.info(f"Final command tree: {', '.join(cmds)}")
        else:
            logger.error("CRITICAL ERROR: Final command tree is empty! Commands failed to register.")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        logger.error(traceback.format_exc())
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="for /help commands"
        )
    )
    
    logger.info("Bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad argument: {error}")
        return
    
    # Log the error
    logger.error(f"Command error in {ctx.command}: {error}")
    logger.error(traceback.format_exc())
    
    # If in debug mode, send the error to the channel
    if DEBUG_MODE:
        await ctx.send(f"An error occurred: {error}")
    else:
        await ctx.send("An error occurred while processing your command. Please try again later.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Handle application command errors."""
    if isinstance(error, discord.app_commands.CommandNotFound):
        return
    
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You don't have permission to use this command.", 
            ephemeral=True
        )
        return
    
    # Log the error
    logger.error(f"App command error: {error}")
    logger.error(traceback.format_exc())
    
    # If in debug mode, send the error details
    if DEBUG_MODE:
        await interaction.response.send_message(
            f"An error occurred: {error}", 
            ephemeral=True
        )
    else:
        # If interaction was already responded to, follow up
        if interaction.response.is_done():
            await interaction.followup.send(
                "An error occurred while processing your command. Please try again later.",
                ephemeral=True
            )
        else:
            # Otherwise respond to the interaction
            await interaction.response.send_message(
                "An error occurred while processing your command. Please try again later.",
                ephemeral=True
            )

async def load_extensions():
    """Load all extensions/cogs."""
    logger.info("Starting extension loading process")
    logger.info("Beginning extension loading sequence")
    
    loaded_count = 0
    total_count = len(INITIAL_EXTENSIONS)
    
    for extension in INITIAL_EXTENSIONS:
        try:
            logger.info(f"Attempting to load extension: {extension}")
            await bot.load_extension(extension)
            logger.info(f"Successfully loaded extension: {extension}")
            loaded_count += 1
        except Exception as e:
            logger.error(f"Failed to load extension {extension}: {e}")
            logger.error(traceback.format_exc())
    
    logger.info(f"Completed extension loading. Loaded {loaded_count} of {total_count} extensions")
    
    # Give a small delay to ensure all commands are registered
    if loaded_count > 0:
        logger.info("Extension loading completed successfully")
        logger.info("Waiting for commands to be fully registered...")
        await asyncio.sleep(1)  # Short delay to ensure all commands are registered
        logger.info("Starting command sync process")
    else:
        logger.error("No extensions were loaded successfully")
        
    return loaded_count > 0

async def main():
    """Main entry point for the bot."""
    try:
        # Load extensions before connecting to Discord
        extensions_loaded = await load_extensions()
        
        if not extensions_loaded:
            logger.error("Failed to load any extensions. Exiting.")
            return 1
        
        # Start the bot
        logger.info("Starting bot...")
        async with bot:
            await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        logger.error(traceback.format_exc())
        return 1
    return 0

if __name__ == "__main__":
    # Run the bot
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 