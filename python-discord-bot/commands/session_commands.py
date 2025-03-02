"""
Session management commands for the Discord bot.
Includes commands for creating, managing, and ending virtual lab sessions.
"""

import os
import uuid
import discord
import logging
import asyncio
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Optional, List

from config import Config
from db_client import SupabaseClient

logger = logging.getLogger('session_commands')

# Create Supabase client
db_client = SupabaseClient()

class SessionCommands(commands.Cog):
    """Commands for managing virtual lab sessions in Discord"""

    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}  # Store active sessions by channel ID

    @app_commands.command(
        name="startlab",
        description="Start a new virtual lab research session"
    )
    @app_commands.describe(
        title="Title of the research session",
        description="Brief description of the session's purpose",
        is_public="Whether the session should be publicly viewable (default: false)"
    )
    async def start_lab(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        description: Optional[str] = None,
        is_public: Optional[bool] = False
    ):
        """
        Start a new virtual lab research session.
        
        Args:
            interaction: The Discord interaction
            title: Title of the session
            description: Brief description of the session's purpose
            is_public: Whether the session should be publicly viewable
        """
        # Check if a session is already active in this channel
        channel_id = str(interaction.channel_id)
        if channel_id in self.active_sessions:
            await interaction.response.send_message(
                "⚠️ A session is already active in this channel. End it first with `/endlab`.",
                ephemeral=True
            )
            return

        try:
            # Create session in database
            session_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "description": description if description else "",
                "isPublic": is_public,
                "userId": str(interaction.user.id),
                "discordChannelId": channel_id,
                "discordGuildId": str(interaction.guild_id),
                "status": "active",
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            }
            
            # First, check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. Please try again later or contact an administrator.",
                    ephemeral=True
                )
                return
            
            # Create session
            created_session = await db_client.create_session(session_data)
            
            # Store active session information
            self.active_sessions[channel_id] = {
                "id": created_session["id"],
                "title": created_session["title"],
                "started_by": interaction.user.id,
                "started_at": datetime.utcnow(),
                "meetings": []  # Will store meeting IDs if any are created
            }
            
            # Create response embed
            embed = discord.Embed(
                title="🧪 Virtual Lab Session Started",
                description=f"**{title}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Description", value=description if description else "No description provided", inline=False)
            embed.add_field(name="Started By", value=interaction.user.mention, inline=True)
            embed.add_field(name="Visibility", value="Public" if is_public else "Private", inline=True)
            embed.add_field(name="Session ID", value=f"`{created_session['id']}`", inline=False)
            embed.add_field(
                name="Available Commands", 
                value="• `/endlab` - End this session\n• `/create_agent` - Create an AI agent\n• `/individual_meeting` - Start a 1:1 meeting with an agent", 
                inline=False
            )
            embed.set_footer(text=f"Started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Session {created_session['id']} created by {interaction.user.name} (ID: {interaction.user.id})")
        
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ Failed to create session: {str(e)}. Please try again later.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="endlab",
        description="End the current virtual lab research session"
    )
    async def end_lab(self, interaction: discord.Interaction):
        """
        End the active virtual lab research session in the current channel.
        
        Args:
            interaction: The Discord interaction
        """
        channel_id = str(interaction.channel_id)
        
        # Check if a session is active in this channel
        if channel_id not in self.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active session found in this channel. Start one with `/startlab`.",
                ephemeral=True
            )
            return
        
        active_session = self.active_sessions[channel_id]
        
        # Check if user has permission to end the session
        # Allow the user who started it or users with manage channel permission
        has_permission = (
            interaction.user.id == active_session["started_by"] or
            interaction.channel.permissions_for(interaction.user).manage_channels
        )
        
        if not has_permission:
            await interaction.response.send_message(
                "⚠️ You don't have permission to end this session. Only the user who started it or users with manage channel permissions can end it.",
                ephemeral=True
            )
            return
        
        try:
            # Update session in database
            session_id = active_session["id"]
            session_data = {
                "status": "completed",
                "updatedAt": datetime.utcnow().isoformat(),
                "endedAt": datetime.utcnow().isoformat()
            }
            
            # First, check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. The session will be ended locally, but the database may not be updated.",
                    ephemeral=True
                )
            else:
                # Update session
                await db_client.update_session(session_id, session_data)
            
            # Calculate session duration
            duration = datetime.utcnow() - active_session["started_at"]
            duration_str = str(duration).split('.')[0]  # Remove microseconds
            
            # Create response embed
            embed = discord.Embed(
                title="🔬 Virtual Lab Session Ended",
                description=f"**{active_session['title']}**",
                color=discord.Color.blue()
            )
            embed.add_field(name="Session ID", value=f"`{session_id}`", inline=True)
            embed.add_field(name="Duration", value=duration_str, inline=True)
            embed.add_field(name="Ended By", value=interaction.user.mention, inline=True)
            
            # Add information about transcript viewing if applicable
            embed.add_field(
                name="View Transcripts", 
                value="Use `/view_transcript` to see the session transcript, or visit the web dashboard.",
                inline=False
            )
            
            embed.set_footer(text=f"Ended at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Session {session_id} ended by {interaction.user.name} (ID: {interaction.user.id})")
            
            # Remove from active sessions
            del self.active_sessions[channel_id]
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ An error occurred while ending the session: {str(e)}. The session may not have been properly closed.",
                ephemeral=False
            )
    
    @app_commands.command(
        name="sessions",
        description="List all active sessions in this server"
    )
    async def list_sessions(self, interaction: discord.Interaction):
        """
        List all active sessions in the current Discord server.
        
        Args:
            interaction: The Discord interaction
        """
        try:
            guild_id = str(interaction.guild_id)
            
            # First, check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. Cannot retrieve sessions.",
                    ephemeral=True
                )
                return
            
            # In a real implementation, we would query the database here
            # For now, we'll just use our local tracking
            guild_sessions = {
                channel_id: session for channel_id, session in self.active_sessions.items()
                if session.get("discordGuildId") == guild_id
            }
            
            if not guild_sessions:
                await interaction.response.send_message(
                    "No active sessions found in this server. Start one with `/startlab`.",
                    ephemeral=True
                )
                return
            
            # Create response embed
            embed = discord.Embed(
                title="🧪 Active Virtual Lab Sessions",
                description=f"Found {len(guild_sessions)} active session(s) in this server:",
                color=discord.Color.green()
            )
            
            for channel_id, session in guild_sessions.items():
                channel = self.bot.get_channel(int(channel_id))
                channel_name = channel.name if channel else "Unknown Channel"
                
                embed.add_field(
                    name=f"{session['title']}",
                    value=f"Channel: {channel_name}\nStarted by: <@{session['started_by']}>\nSession ID: `{session['id']}`",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ An error occurred while listing sessions: {str(e)}.",
                ephemeral=True
            )

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(
        SessionCommands(bot),
        guilds=[discord.Object(id=guild.id) for guild in bot.guilds]
    ) 