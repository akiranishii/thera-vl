"""
Transcript commands for the Discord bot.
Handles viewing and managing transcripts from meetings.
"""

import asyncio
import discord
import logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional, List, Dict, Any

from db_client import SupabaseClient

# Set up logging
logger = logging.getLogger('transcript')

# Create client
db_client = SupabaseClient()

class TranscriptCommands(commands.Cog):
    """Commands for viewing and managing transcripts from research sessions"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(
        name="view_transcript",
        description="View the transcript of a completed meeting"
    )
    @app_commands.describe(
        meeting_id="ID of the meeting to view",
        format="Output format (full or summary)",
        export="Export the transcript to a file (true/false)"
    )
    async def view_transcript(
        self,
        interaction: discord.Interaction,
        meeting_id: str,
        format: Optional[str] = "full",
        export: Optional[bool] = False
    ):
        """
        View the transcript of a completed meeting
        
        Args:
            interaction: The Discord interaction
            meeting_id: ID of the meeting to view
            format: Output format (full or summary)
            export: Whether to export the transcript to a file
        """
        # Defer response since this might take a while
        await interaction.response.defer(thinking=True)
        
        try:
            # Get the meeting
            meeting = await db_client.get_meeting(meeting_id)
            
            if not meeting:
                await interaction.followup.send(
                    f"⚠️ Meeting with ID {meeting_id} not found.",
                    ephemeral=True
                )
                return
                
            # Get the transcripts
            transcripts = await db_client.get_transcripts_by_meeting(meeting_id)
            
            if not transcripts:
                await interaction.followup.send(
                    f"⚠️ No transcript entries found for meeting {meeting_id}.",
                    ephemeral=True
                )
                return
                
            # Sort transcripts by timestamp
            sorted_transcripts = sorted(transcripts, key=lambda t: t["timestamp"])
            
            # Create the main embed
            embed = discord.Embed(
                title=f"📝 Meeting Transcript",
                description=f"**{meeting['title']}**\n{meeting['agenda']}",
                color=discord.Color.blue()
            )
            
            # Add meeting details
            embed.add_field(name="Meeting Type", value=meeting["type"].capitalize(), inline=True)
            embed.add_field(name="Status", value=meeting["status"].capitalize(), inline=True)
            embed.add_field(name="Meeting ID", value=meeting_id, inline=True)
            
            # Add timestamps
            started_at = datetime.fromisoformat(meeting["startedAt"].replace("Z", "+00:00"))
            embed.add_field(
                name="Started",
                value=f"<t:{int(started_at.timestamp())}:f>",
                inline=True
            )
            
            if meeting.get("endedAt"):
                ended_at = datetime.fromisoformat(meeting["endedAt"].replace("Z", "+00:00"))
                embed.add_field(
                    name="Ended",
                    value=f"<t:{int(ended_at.timestamp())}:f>",
                    inline=True
                )
                
                # Calculate duration
                duration = ended_at - started_at
                minutes = int(duration.total_seconds() / 60)
                embed.add_field(
                    name="Duration",
                    value=f"{minutes} minutes",
                    inline=True
                )
            
            # Add summary if available
            if meeting.get("summary"):
                embed.add_field(
                    name="Summary",
                    value=meeting["summary"][:1024],
                    inline=False
                )
                
                # If summary format is requested, just show the summary
                if format.lower() == "summary":
                    embed.add_field(
                        name="Transcript Format",
                        value="Showing summary only. Use `/view_transcript meeting_id:{meeting_id} format:full` to see the full transcript.",
                        inline=False
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Send the main embed
            await interaction.followup.send(embed=embed)
            
            # Handle export if requested
            if export:
                # Create an export file
                export_filename = f"transcript_{meeting_id}_{int(datetime.utcnow().timestamp())}.txt"
                with open(export_filename, "w") as file:
                    file.write(f"TRANSCRIPT: {meeting['title']}\n")
                    file.write(f"AGENDA: {meeting['agenda']}\n")
                    file.write(f"MEETING ID: {meeting_id}\n")
                    file.write(f"DATE: {started_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
                    
                    for entry in sorted_transcripts:
                        role = entry["role"]
                        content = entry["content"]
                        agent_name = entry["agentName"] if "agentName" in entry else "Unknown"
                        timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00")).strftime('%H:%M:%S')
                        
                        # Skip system entries (like summaries) unless it's specifically requested
                        if role == "system" and agent_name == "System" and format.lower() != "full":
                            continue
                        
                        # Format based on role
                        if role == "user":
                            formatted_entry = f"[{timestamp}] {agent_name}: {content}"
                        elif role == "assistant":
                            formatted_entry = f"[{timestamp}] {agent_name}: {content}"
                        elif role == "critic":
                            formatted_entry = f"[{timestamp}] {agent_name} (Critic): {content}"
                        else:
                            formatted_entry = f"[{timestamp}] {agent_name}: {content}"
                            
                        file.write(f"{formatted_entry}\n\n")
                
                # Send the file
                await interaction.channel.send(
                    f"📄 Transcript export for meeting {meeting_id}:",
                    file=discord.File(export_filename)
                )
                
                # Clean up the file
                import os
                os.remove(export_filename)
                
                # If export only, don't send the transcript chunks
                if format.lower() == "export":
                    return
            
            # If format is summary, don't show the full transcript
            if format.lower() == "summary":
                return
            
            # Process and send transcript chunks for full format
            current_chunk = ""
            current_speaker = None
            messages_to_send = []
            
            for entry in sorted_transcripts:
                role = entry["role"]
                content = entry["content"]
                agent_name = entry["agentName"] if "agentName" in entry else "Unknown"
                
                # Skip system entries (like summaries)
                if role == "system" and agent_name == "System":
                    continue
                
                # Format based on role
                if role == "user":
                    formatted_entry = f"👤 **{agent_name}:** {content}"
                elif role == "assistant":
                    formatted_entry = f"🤖 **{agent_name}:** {content}"
                elif role == "critic":
                    formatted_entry = f"🔍 **{agent_name} (Critic):** {content}"
                else:
                    formatted_entry = f"⚙️ **{agent_name}:** {content}"
                
                # Check if we need to create a new chunk
                if len(current_chunk) + len(formatted_entry) > 2000 or current_speaker != agent_name:
                    if current_chunk:
                        messages_to_send.append(current_chunk)
                    current_chunk = formatted_entry
                    current_speaker = agent_name
                else:
                    current_chunk += "\n\n" + formatted_entry
            
            # Add the last chunk if not empty
            if current_chunk:
                messages_to_send.append(current_chunk)
            
            # Send all chunks, ensuring we don't exceed rate limits
            for i, chunk in enumerate(messages_to_send):
                # Add pagination info
                paginated_chunk = f"{chunk}\n\n*Page {i+1}/{len(messages_to_send)}*"
                
                # Send the chunk
                await interaction.channel.send(paginated_chunk)
                
                # Add a small delay to avoid rate limiting
                if i < len(messages_to_send) - 1:
                    await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error retrieving transcript: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while retrieving the transcript: {str(e)}.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="list_transcripts",
        description="List available transcripts from recent meetings"
    )
    @app_commands.describe(
        session_id="Optional: Filter by session ID",
        limit="Maximum number of transcripts to show (default: 10)"
    )
    async def list_transcripts(
        self,
        interaction: discord.Interaction,
        session_id: Optional[str] = None,
        limit: Optional[int] = 10
    ):
        """
        List available transcripts from recent meetings
        
        Args:
            interaction: The Discord interaction
            session_id: Optional session ID to filter by
            limit: Maximum number of transcripts to show
        """
        await interaction.response.defer(thinking=True)
        
        try:
            # Get sessions to list
            meetings = []
            
            if session_id:
                # If session ID provided, get meetings for that session
                meetings = await db_client.get_meetings_by_session(session_id)
            else:
                # Otherwise, get recent meetings (this depends on what's available in db_client)
                # This might need to be implemented in db_client
                # For now, let's check if such a method exists, and if not, inform the user
                if hasattr(db_client, "get_recent_meetings"):
                    meetings = await db_client.get_recent_meetings(limit)
                else:
                    await interaction.followup.send(
                        "⚠️ Listing all recent meetings is not supported yet. Please provide a session ID.",
                        ephemeral=True
                    )
                    return
            
            if not meetings:
                await interaction.followup.send(
                    f"No meeting transcripts found{' for the specified session' if session_id else ''}.",
                    ephemeral=True
                )
                return
            
            # Create an embed to display the meetings
            embed = discord.Embed(
                title="📝 Available Transcripts",
                description=f"Use `/view_transcript meeting_id:<ID>` to view a transcript",
                color=discord.Color.blue()
            )
            
            # Sort meetings by date (most recent first)
            sorted_meetings = sorted(
                meetings, 
                key=lambda m: m.get("startedAt", ""), 
                reverse=True
            )[:limit]
            
            # Add each meeting to the embed
            for idx, meeting in enumerate(sorted_meetings):
                meeting_id = meeting.get("id", "Unknown")
                title = meeting.get("title", "Untitled Meeting")
                meeting_type = meeting.get("type", "unknown").capitalize()
                status = meeting.get("status", "unknown").capitalize()
                
                # Format the date
                started_at = "Unknown"
                if meeting.get("startedAt"):
                    try:
                        date_obj = datetime.fromisoformat(meeting["startedAt"].replace("Z", "+00:00"))
                        started_at = f"<t:{int(date_obj.timestamp())}:f>"
                    except:
                        started_at = meeting["startedAt"]
                
                # Add field for this meeting
                embed.add_field(
                    name=f"{idx+1}. {title}",
                    value=f"**ID:** {meeting_id}\n**Type:** {meeting_type}\n**Status:** {status}\n**Date:** {started_at}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing transcripts: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while listing transcripts: {str(e)}.",
                ephemeral=True
            )

async def setup(bot):
    """Add the cog to the bot - Discord.py extension standard"""
    await bot.add_cog(TranscriptCommands(bot)) 