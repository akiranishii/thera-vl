"""
Brainstorming commands for the Discord bot.
Includes commands for conducting multi-agent brainstorming sessions.
"""

import os
import uuid
import discord
import logging
import asyncio
import json
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any, Literal

from config import Config
from db_client import SupabaseClient
from llm_client import LLMClient
from orchestrator import BrainstormOrchestrator
from models import get_system_prompt, get_default_model_for_provider

logger = logging.getLogger('brainstorm_commands')

# Create clients
db_client = SupabaseClient()
llm_client = LLMClient()
orchestrator = BrainstormOrchestrator(db_client, llm_client)

class BrainstormCommands(commands.Cog):
    """Commands for conducting multi-agent brainstorming sessions"""

    def __init__(self, bot):
        self.bot = bot
        self.session_cog = None
        self.agent_cog = None
        self.active_brainstorms = {}  # Store active brainstorms by channel ID
        
    async def cog_load(self):
        """Find the necessary cogs for accessing active sessions and agents"""
        self.session_cog = self.bot.get_cog("SessionCommands")
        if not self.session_cog:
            logger.error("SessionCommands cog not found. Brainstorming commands may not work properly.")
            
        self.agent_cog = self.bot.get_cog("AgentCommands")
        if not self.agent_cog:
            logger.error("AgentCommands cog not found. Brainstorming commands may not work properly.")

    @app_commands.command(
        name="brainstorm",
        description="Conduct a multi-agent brainstorming session on a research topic"
    )
    @app_commands.describe(
        agenda="The main research topic or question to brainstorm",
        agent_count="Number of agents to include (default: 3)",
        rounds="Number of rounds of discussion (default: 3)",
        include_critic="Whether to include Critic feedback (default: true)",
        agent_list="Comma-separated list of specific agent names to include (optional)",
        agenda_questions="Additional bullet points or clarifications",
        rules="Extra constraints or instructions",
        parallel_meetings="Number of parallel meetings to run with different agent combinations (default: 1)"
    )
    async def brainstorm(
        self, 
        interaction: discord.Interaction, 
        agenda: str,
        agent_count: Optional[int] = 3,
        rounds: Optional[int] = 3,
        include_critic: Optional[bool] = True,
        agent_list: Optional[str] = None,
        agenda_questions: Optional[str] = None,
        rules: Optional[str] = None,
        parallel_meetings: Optional[int] = 1
    ):
        """
        Conduct a multi-agent brainstorming session with AI research agents.
        
        Args:
            interaction: The Discord interaction
            agenda: The main research topic or question
            agent_count: Number of agents to include (default: 3)
            rounds: Number of rounds of discussion (default: 3)
            include_critic: Whether to include Critic feedback (default: true)
            agent_list: Comma-separated list of specific agent names to include (optional)
            agenda_questions: Additional bullet points or clarifications
            rules: Extra constraints or instructions
            parallel_meetings: Number of parallel meetings to run with different agent combinations (default: 1)
        """
        # Check if a session is active in this channel
        channel_id = str(interaction.channel_id)
        if not self.session_cog or not hasattr(self.session_cog, "active_sessions"):
            await interaction.response.send_message(
                "⚠️ Could not access session information. Please try again later.",
                ephemeral=True
            )
            return
            
        if channel_id not in self.session_cog.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active session found in this channel. Start one with `/startlab`.",
                ephemeral=True
            )
            return
            
        active_session = self.session_cog.active_sessions[channel_id]
        session_id = active_session["id"]
        
        # Check DB connection
        connection_ok = await db_client.check_connection()
        if not connection_ok:
            await interaction.response.send_message(
                "⚠️ Failed to connect to the database. Please try again later.",
                ephemeral=True
            )
            return
            
        # Defer response since this might take a while
        await interaction.response.defer(thinking=True)
        
        try:
            # Get all available agents for this session
            all_agents = await db_client.get_agents({"sessionId": session_id})
            
            if not all_agents:
                await interaction.followup.send(
                    "⚠️ No agents found in this session. Please create some agents first with `/create_agent` or `/generate_agents`.",
                    ephemeral=True
                )
                return
                
            # Determine which agents to include
            selected_agents = []
            
            if agent_list:
                # Parse the comma-separated list of agent names
                requested_names = [name.strip() for name in agent_list.split(',')]
                
                # Find matching agents
                for name in requested_names:
                    agent = next((a for a in all_agents if a["name"].lower() == name.lower()), None)
                    if agent:
                        selected_agents.append(agent)
                
                if not selected_agents:
                    await interaction.followup.send(
                        f"⚠️ None of the specified agents ({agent_list}) were found. Please check agent names and try again.",
                        ephemeral=True
                    )
                    return
                    
                if len(selected_agents) < 2:
                    await interaction.followup.send(
                        f"⚠️ At least 2 agents are required for a brainstorming session. Only found: {selected_agents[0]['name']}",
                        ephemeral=True
                    )
                    return
            else:
                # Auto-select agents based on count
                # First, filter out any critic agents (they're handled separately)
                non_critic_agents = [a for a in all_agents if a.get("role", "").lower() != "critic"]
                
                if len(non_critic_agents) < 2:
                    await interaction.followup.send(
                        f"⚠️ At least 2 non-critic agents are required for a brainstorming session. Please create more agents.",
                        ephemeral=True
                    )
                    return
                
                # Sort agents to prioritize Principal Investigators first, then diverse roles
                sorted_agents = sorted(
                    non_critic_agents,
                    key=lambda a: 0 if a.get("role", "").lower() == "principal investigator" else 1
                )
                
                # Select up to agent_count agents
                selected_agents = sorted_agents[:min(agent_count, len(sorted_agents))]
            
            # Create initial embed to track progress
            embed = discord.Embed(
                title=f"🧠 Brainstorming Session",
                description=f"**Topic:** {agenda}",
                color=discord.Color.blue()
            )
            
            # Add agents to the embed
            agent_names = [f"{a['name']} ({a.get('role', 'Scientist')})" for a in selected_agents]
            embed.add_field(
                name="Participating Agents", 
                value="\n".join([f"• {name}" for name in agent_names]),
                inline=False
            )
            
            # Add session details
            embed.add_field(name="Rounds", value=f"{rounds}", inline=True)
            embed.add_field(name="Critic", value="Enabled" if include_critic else "Disabled", inline=True)
            
            if parallel_meetings > 1:
                embed.add_field(name="Parallel Meetings", value=f"{parallel_meetings}", inline=True)
            
            if agenda_questions:
                embed.add_field(name="Additional Questions", value=agenda_questions, inline=False)
                
            if rules:
                embed.add_field(name="Rules", value=rules, inline=False)
                
            embed.add_field(name="Status", value="Starting...", inline=False)
            
            # Send initial response that we'll update
            message = await interaction.followup.send(embed=embed)
            
            # Track all meeting IDs created for this brainstorm command
            meeting_ids = []
            all_selected_agents = []
            
            # If parallel_meetings > 1, we need different agent combinations for each meeting
            for meeting_index in range(parallel_meetings):
                # For the first meeting, use the already selected agents
                if meeting_index == 0:
                    meeting_agents = selected_agents
                else:
                    # For additional meetings, randomly select different combinations
                    # but maintain at least some diversity in roles and expertise
                    if agent_list:
                        # If specific agents were requested, use subsets of them for parallel meetings
                        import random
                        # Get at least half of the requested agents for each parallel meeting
                        min_agents = max(2, len(selected_agents) // 2)
                        subset_size = random.randint(min_agents, len(selected_agents))
                        meeting_agents = random.sample(selected_agents, subset_size)
                    else:
                        # If auto-selecting agents, get a different set for each meeting
                        # Ensure we don't reuse agents if possible
                        used_agent_ids = [a["id"] for agents_list in all_selected_agents for a in agents_list]
                        unused_agents = [a for a in all_agents if a["id"] not in used_agent_ids and a.get("role", "").lower() != "critic"]
                        
                        # If we've used all agents, start recycling with different combinations
                        if len(unused_agents) < agent_count:
                            unused_agents = non_critic_agents
                            
                        # Sort agents to prioritize Principal Investigators first, then diverse roles
                        sorted_agents = sorted(
                            unused_agents,
                            key=lambda a: 0 if a.get("role", "").lower() == "principal investigator" else 1
                        )
                        
                        # Select up to agent_count agents
                        meeting_agents = sorted_agents[:min(agent_count, len(sorted_agents))]
                
                # Track all selected agents
                all_selected_agents.append(meeting_agents)
                
                # Create meeting ID and record
                meeting_id = str(uuid.uuid4())
                meeting_ids.append(meeting_id)
                
                # Create suffix for parallel meetings
                meeting_suffix = f" (Variant {meeting_index + 1})" if parallel_meetings > 1 else ""
                
                # Create meeting record in the database
                meeting_data = {
                    "id": meeting_id,
                    "sessionId": session_id,
                    "type": "brainstorm",
                    "title": f"Brainstorming on {agenda}{meeting_suffix}",
                    "agenda": agenda,
                    "agendaQuestions": agenda_questions if agenda_questions else "",
                    "rules": rules if rules else "",
                    "startedAt": datetime.utcnow().isoformat(),
                    "status": "active",
                    "metadata": {
                        "agent_count": len(meeting_agents),
                        "rounds": rounds,
                        "include_critic": include_critic,
                        "agents": [a["id"] for a in meeting_agents],
                        "parallel_index": meeting_index,
                        "parallel_total": parallel_meetings
                    },
                    "createdBy": str(interaction.user.id),
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
                
                await db_client.create_meeting(meeting_data)
            
            # Add meetings to active brainstorms - we'll track all parallel meetings
            self.active_brainstorms[channel_id] = {
                "meeting_ids": meeting_ids,
                "message_id": message.id,
                "all_agents": all_selected_agents,
                "rounds": rounds,
                "parallel_meetings": parallel_meetings,
                "completed_meetings": 0
            }
            
            # Create progress update callback that handles parallel meetings
            async def update_progress(current_round, total_rounds, status_text, meeting_index=0):
                try:
                    progress_embed = discord.Embed(
                        title=f"🧠 Brainstorming Session",
                        description=f"**Topic:** {agenda}",
                        color=discord.Color.blue()
                    )
                    
                    # Show progress for parallel meetings
                    if parallel_meetings > 1:
                        progress_embed.add_field(
                            name="Parallel Sessions",
                            value=f"Running {parallel_meetings} variations with different agent combinations",
                            inline=False
                        )
                        
                        # Add overall progress
                        completed = self.active_brainstorms[channel_id]["completed_meetings"]
                        progress_embed.add_field(
                            name="Overall Progress", 
                            value=f"Completed {completed}/{parallel_meetings} sessions",
                            inline=True
                        )
                        
                        # Add current session info
                        progress_embed.add_field(
                            name="Current Session", 
                            value=f"Variant {meeting_index + 1}/{parallel_meetings}",
                            inline=True
                        )
                    
                    # Add agents for current meeting
                    agent_names = [f"{a['name']} ({a.get('role', 'Scientist')})" for a in all_selected_agents[meeting_index]]
                    progress_embed.add_field(
                        name=f"{'Current ' if parallel_meetings > 1 else ''}Participating Agents", 
                        value="\n".join([f"• {name}" for name in agent_names]),
                        inline=False
                    )
                    
                    # Add progress bar for current meeting
                    if total_rounds > 0:
                        progress = int((current_round / total_rounds) * 10)
                        progress_bar = "█" * progress + "░" * (10 - progress)
                        percentage = int((current_round / total_rounds) * 100)
                        progress_embed.add_field(
                            name=f"Progress: {percentage}%", 
                            value=f"`{progress_bar}` Round {current_round}/{total_rounds}",
                            inline=False
                        )
                    
                    # Add status
                    progress_embed.add_field(name="Status", value=status_text, inline=False)
                    progress_embed.set_footer(text=f"Meeting ID: {meeting_ids[meeting_index]}")
                    
                    await message.edit(embed=progress_embed)
                except Exception as e:
                    logger.error(f"Error updating progress: {str(e)}")
            
            # Start the brainstorming session
            try:
                # For parallel meetings, we need to run them one by one
                for meeting_index in range(parallel_meetings):
                    current_meeting_id = meeting_ids[meeting_index]
                    current_agents = all_selected_agents[meeting_index]
                    
                    # Update message to show which meeting is currently running
                    if parallel_meetings > 1:
                        await update_progress(0, rounds, f"Starting variant {meeting_index + 1}/{parallel_meetings}...", meeting_index)
                    
                    # Run the brainstorming session with the current set of agents
                    transcript_data = await orchestrator.run_brainstorm(
                        session_id=session_id,
                        meeting_id=current_meeting_id,
                        agents=current_agents,
                        agenda=agenda,
                        rounds=rounds,
                        include_critic=include_critic,
                        agenda_questions=agenda_questions,
                        rules=rules,
                        progress_callback=lambda current, total, status: update_progress(current, total, status, meeting_index)
                    )
                    
                    # Increment completed meetings count
                    if channel_id in self.active_brainstorms:
                        self.active_brainstorms[channel_id]["completed_meetings"] += 1
                
                # All meetings have been completed, show final results
                if parallel_meetings > 1:
                    # Create a summary of all meetings
                    final_embed = discord.Embed(
                        title=f"🧠 Multiple Brainstorming Sessions Complete",
                        description=f"**Topic:** {agenda}",
                        color=discord.Color.green()
                    )
                    
                    final_embed.add_field(
                        name="Sessions Completed", 
                        value=f"{parallel_meetings} parallel brainstorming sessions",
                        inline=False
                    )
                    
                    final_embed.add_field(name="Rounds per Session", value=f"{rounds}", inline=True)
                    final_embed.add_field(name="Include Critic", value="Yes" if include_critic else "No", inline=True)
                    
                    # Add meeting IDs for viewing transcripts
                    meeting_links = "\n".join([f"• Variant {i+1}: `/view_transcript meeting_id:{mid}`" for i, mid in enumerate(meeting_ids)])
                    final_embed.add_field(
                        name="View Transcripts", 
                        value=meeting_links,
                        inline=False
                    )
                    
                    # Add a note about comparing results
                    final_embed.add_field(
                        name="Compare Results", 
                        value="Use the transcript commands above to compare insights from different agent combinations.",
                        inline=False
                    )
                    
                    final_embed.set_footer(text=f"Completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    
                    await message.edit(embed=final_embed)
                else:
                    # For single meetings, show the standard summary
                    meeting = await db_client.get_meeting(meeting_ids[0])
                    summary = meeting.get("summary", "No summary available.")
                    
                    final_embed = discord.Embed(
                        title=f"🧠 Brainstorming Session Complete",
                        description=f"**Topic:** {agenda}",
                        color=discord.Color.green()
                    )
                    
                    final_embed.add_field(
                        name="Participating Agents", 
                        value="\n".join([f"• {a['name']} ({a.get('role', 'Scientist')})" for a in all_selected_agents[0]]),
                        inline=False
                    )
                    
                    final_embed.add_field(name="Rounds", value=f"{rounds} completed", inline=True)
                    final_embed.add_field(name="Meeting ID", value=meeting_ids[0], inline=True)
                    
                    # Add summary
                    final_embed.add_field(name="Summary", value=summary[:1024], inline=False)
                    
                    # Add view transcript info
                    final_embed.add_field(
                        name="View Full Transcript", 
                        value=f"Use `/view_transcript meeting_id:{meeting_ids[0]}` to see the complete conversation",
                        inline=False
                    )
                    
                    final_embed.set_footer(text=f"Completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    
                    await message.edit(embed=final_embed)
                
                # Remove from active brainstorms
                if channel_id in self.active_brainstorms:
                    del self.active_brainstorms[channel_id]
                    
                logger.info(f"Brainstorming sessions completed: {', '.join(meeting_ids)}")
                
            except Exception as e:
                logger.error(f"Error during brainstorming session: {str(e)}")
                error_embed = discord.Embed(
                    title=f"🧠 Brainstorming Session Error",
                    description=f"**Topic:** {agenda}",
                    color=discord.Color.red()
                )
                
                error_embed.add_field(name="Error", value=str(e), inline=False)
                error_embed.set_footer(text=f"Meeting IDs: {', '.join(meeting_ids[:3])}...")
                
                await message.edit(embed=error_embed)
                
                # Update all active meeting records with error status
                for mid in meeting_ids:
                    await db_client.update_meeting(mid, {
                        "endedAt": datetime.utcnow().isoformat(),
                        "status": "error",
                        "updatedAt": datetime.utcnow().isoformat()
                    })
                
                # Remove from active brainstorms
                if channel_id in self.active_brainstorms:
                    del self.active_brainstorms[channel_id]
        
        except Exception as e:
            logger.error(f"Error setting up brainstorming session: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while setting up the brainstorming session: {str(e)}.",
                ephemeral=True
            )

    @app_commands.command(
        name="cancel_brainstorm",
        description="Cancel an active brainstorming session"
    )
    async def cancel_brainstorm(
        self,
        interaction: discord.Interaction
    ):
        """
        Cancel an active brainstorming session in the current channel
        
        Args:
            interaction: The Discord interaction
        """
        channel_id = str(interaction.channel_id)
        
        # Check if there's an active brainstorm in this channel
        if channel_id not in self.active_brainstorms:
            await interaction.response.send_message(
                "⚠️ No active brainstorming session found in this channel.",
                ephemeral=True
            )
            return
        
        # Get the active brainstorm info
        active_brainstorm = self.active_brainstorms[channel_id]
        meeting_ids = active_brainstorm.get("meeting_ids", [])
        
        if not meeting_ids:
            await interaction.response.send_message(
                "⚠️ Could not find meeting IDs for the active brainstorming session.",
                ephemeral=True
            )
            return
        
        # Defer response since canceling might take a moment
        await interaction.response.defer(thinking=True)
        
        canceled_count = 0
        failed_count = 0
        
        # Cancel each meeting
        for meeting_id in meeting_ids:
            success = await orchestrator.cancel_brainstorm(meeting_id)
            if success:
                canceled_count += 1
            else:
                failed_count += 1
        
        # Remove from active brainstorms
        del self.active_brainstorms[channel_id]
        
        # Send confirmation
        if canceled_count > 0:
            await interaction.followup.send(
                f"✅ Successfully canceled {canceled_count} brainstorming session(s)." + 
                (f" Failed to cancel {failed_count} session(s)." if failed_count > 0 else ""),
                ephemeral=False
            )
        else:
            await interaction.followup.send(
                "⚠️ Failed to cancel any brainstorming sessions. They may have already completed or encountered errors.",
                ephemeral=True
            )

    @app_commands.command(
        name="compare_brainstorms",
        description="Compare the results of multiple brainstorming sessions"
    )
    @app_commands.describe(
        meeting_ids="Comma-separated list of meeting IDs to compare"
    )
    async def compare_brainstorms(
        self,
        interaction: discord.Interaction,
        meeting_ids: str
    ):
        """
        Compare the results of multiple brainstorming sessions
        
        Args:
            interaction: The Discord interaction
            meeting_ids: Comma-separated list of meeting IDs to compare
        """
        # Parse the meeting IDs
        ids_list = [id.strip() for id in meeting_ids.split(',')]
        
        if len(ids_list) < 2:
            await interaction.response.send_message(
                "⚠️ Please provide at least two meeting IDs to compare.",
                ephemeral=True
            )
            return
            
        if len(ids_list) > 5:
            await interaction.response.send_message(
                "⚠️ You can compare a maximum of 5 meetings at once.",
                ephemeral=True
            )
            return
        
        # Defer response since fetching and comparing might take time
        await interaction.response.defer(thinking=True)
        
        try:
            # Fetch all meetings
            meetings = []
            for meeting_id in ids_list:
                meeting = await db_client.get_meeting(meeting_id)
                if meeting:
                    meetings.append(meeting)
                    
            if len(meetings) < 2:
                await interaction.followup.send(
                    "⚠️ Could not find at least two valid meetings with the provided IDs.",
                    ephemeral=True
                )
                return
                
            # Create embed for comparison
            embed = discord.Embed(
                title="🔄 Brainstorming Session Comparison",
                description="Comparing insights across multiple brainstorming sessions",
                color=discord.Color.gold()
            )
            
            # Check if meetings are related (same topic/agenda)
            agendas = set(m.get("agenda", "") for m in meetings)
            if len(agendas) == 1:
                embed.add_field(
                    name="Research Topic",
                    value=next(iter(agendas)),
                    inline=False
                )
            else:
                # If comparing different topics, show each
                for idx, meeting in enumerate(meetings):
                    embed.add_field(
                        name=f"Topic {idx+1}",
                        value=meeting.get("agenda", "Unknown"),
                        inline=True
                    )
            
            # Add meeting IDs for reference
            embed.add_field(
                name="Meeting IDs",
                value="\n".join([f"• {m['id']}" for m in meetings]),
                inline=False
            )
            
            # Create a comparison prompt for the LLM
            summaries = []
            for meeting in meetings:
                summary = meeting.get("summary", "No summary available")
                meeting_id = meeting.get("id", "Unknown")
                variant = meeting.get("metadata", {}).get("parallel_index", 0) + 1
                summaries.append(f"Session {variant} (ID: {meeting_id}):\n{summary}")
            
            # Send the initial embed
            await interaction.followup.send(embed=embed)
            
            # Generate a comparison with the LLM
            system_prompt = """You are a research meta-analyst. Your task is to compare multiple brainstorming
sessions on the same or related topics. Focus on:

1. Key similarities and differences in ideas proposed
2. Unique insights from each session
3. How different agent combinations led to different outcomes
4. Which session(s) produced the most innovative or valuable insights
5. How the insights could be synthesized into a stronger combined approach

Be objective in your analysis and specific about the strengths of each session."""
            
            comparison_prompt = f"""Compare the following brainstorming session summaries and analyze the different perspectives and insights:

{'-' * 40}
{'\n\n'.join(summaries)}
{'-' * 40}

Provide a comprehensive comparison highlighting unique contributions from each session and how they complement each other."""
            
            comparison_conversation = [{"role": "user", "content": comparison_prompt}]
            
            try:
                comparison_response = await llm_client.chat_with_history(
                    provider="anthropic",  # Default to Anthropic for complex reasoning
                    conversation=comparison_conversation,
                    system_prompt=system_prompt
                )
                
                # Split response into manageable chunks for Discord
                analysis = comparison_response["text"]
                
                # Create a more detailed embed
                analysis_embed = discord.Embed(
                    title="📊 Brainstorming Comparison Analysis",
                    description="Detailed analysis of the different sessions",
                    color=discord.Color.blue()
                )
                
                # Send chunks of the analysis (Discord has a 1024 character limit per field)
                chunk_size = 1024
                if len(analysis) <= chunk_size:
                    analysis_embed.add_field(
                        name="Analysis",
                        value=analysis,
                        inline=False
                    )
                    await interaction.channel.send(embed=analysis_embed)
                else:
                    # Split into introduction and key points
                    parts = []
                    remaining = analysis
                    
                    while remaining:
                        # Try to find natural break points
                        if len(remaining) <= chunk_size:
                            parts.append(remaining)
                            break
                            
                        # Find the last period or newline before the chunk_size
                        last_period = remaining[:chunk_size].rfind(".")
                        last_newline = remaining[:chunk_size].rfind("\n")
                        
                        # Use the later of the two break points
                        break_point = max(last_period, last_newline)
                        
                        # If no good break point, just use chunk_size
                        if break_point == -1:
                            break_point = chunk_size - 1
                            
                        # Add 1 to include the break character
                        parts.append(remaining[:break_point + 1])
                        remaining = remaining[break_point + 1:].strip()
                    
                    # Send the first part in the primary embed
                    analysis_embed.add_field(
                        name="Analysis (Part 1)",
                        value=parts[0],
                        inline=False
                    )
                    await interaction.channel.send(embed=analysis_embed)
                    
                    # Send remaining parts as follow-up messages
                    for i, part in enumerate(parts[1:], 2):
                        part_embed = discord.Embed(
                            title=f"📊 Analysis (Part {i}/{len(parts)})",
                            description=part,
                            color=discord.Color.blue()
                        )
                        await interaction.channel.send(embed=part_embed)
                
            except Exception as e:
                logger.error(f"Error generating comparison: {str(e)}")
                await interaction.channel.send(
                    f"⚠️ Error generating comparison: {str(e)}. Please view the individual meeting transcripts instead."
                )
                
        except Exception as e:
            logger.error(f"Error comparing brainstorms: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while comparing the brainstorming sessions: {str(e)}",
                ephemeral=True
            )

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(
        BrainstormCommands(bot),
        guilds=[discord.Object(id=guild.id) for guild in bot.guilds]
    ) 