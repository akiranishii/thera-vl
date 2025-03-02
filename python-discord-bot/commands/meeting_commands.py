"""
Meeting management commands for the Discord bot.
Includes commands for conducting individual meetings with AI research agents.
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
from models import get_system_prompt_for_role, get_default_model_for_provider

logger = logging.getLogger('meeting_commands')

# Create Supabase client
db_client = SupabaseClient()

# Create LLM client
llm_client = LLMClient()

class MeetingCommands(commands.Cog):
    """Commands for conducting meetings with AI research agents"""

    def __init__(self, bot):
        self.bot = bot
        self.session_cog = None
        self.agent_cog = None
        self.active_meetings = {}  # Store active meetings by channel ID
        
    async def cog_load(self):
        """Find the necessary cogs for accessing active sessions and agents"""
        self.session_cog = self.bot.get_cog("SessionCommands")
        if not self.session_cog:
            logger.error("SessionCommands cog not found. Meeting commands may not work properly.")
            
        self.agent_cog = self.bot.get_cog("AgentCommands")
        if not self.agent_cog:
            logger.error("AgentCommands cog not found. Meeting commands may not work properly.")

    @app_commands.command(
        name="individual_meeting",
        description="Conduct a one-on-one discussion with a specific AI agent"
    )
    @app_commands.describe(
        agent_name="Name of the agent to meet with",
        agenda="The specific topic or question for this agent",
        rounds="Number of interaction rounds (default: 3)",
        include_critic="Whether to include Critic feedback after each agent response (default: false)",
        agenda_questions="Additional bullet points or clarifications",
        rules="Extra constraints or instructions"
    )
    async def individual_meeting(
        self, 
        interaction: discord.Interaction, 
        agent_name: str,
        agenda: str,
        rounds: Optional[int] = 3,
        include_critic: Optional[bool] = False,
        agenda_questions: Optional[str] = None,
        rules: Optional[str] = None
    ):
        """
        Conduct a one-on-one discussion with a specified agent, optionally including Critic feedback.
        
        Args:
            interaction: The Discord interaction
            agent_name: Name of the agent to meet with
            agenda: The specific topic or question for this agent
            rounds: Number of interaction rounds (default: 3)
            include_critic: Whether to include Critic feedback after each agent response
            agenda_questions: Additional bullet points or clarifications
            rules: Extra constraints or instructions
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
        
        # Find the specified agent
        try:
            agents = await db_client.get_agents({"sessionId": session_id})
            target_agent = next((a for a in agents if a["name"].lower() == agent_name.lower()), None)
            
            if not target_agent:
                await interaction.followup.send(
                    f"⚠️ Agent '{agent_name}' not found. Please create it first with `/create_agent`.",
                    ephemeral=True
                )
                return
                
            # If include_critic is true, check if a critic agent exists
            critic_agent = None
            if include_critic:
                critic_agent = next((a for a in agents if a["role"] == "Critic"), None)
                if not critic_agent:
                    # Use a default critic if none exists
                    critic_agent = {
                        "id": str(uuid.uuid4()),
                        "name": "Scientific Critic",
                        "role": "Critic",
                        "expertise": "Critical analysis and evaluation",
                        "goal": "Identify flaws, suggest improvements, and ensure scientific rigor",
                        "model": "anthropic",  # Default provider
                        "sessionId": session_id
                    }
            
            # Create meeting record
            meeting_id = str(uuid.uuid4())
            meeting_data = {
                "id": meeting_id,
                "sessionId": session_id,
                "type": "individual",
                "title": f"Meeting with {agent_name} on {agenda}",
                "agenda": agenda,
                "agendaQuestions": agenda_questions if agenda_questions else "",
                "rules": rules if rules else "",
                "startedAt": datetime.utcnow().isoformat(),
                "status": "active",
                "createdBy": str(interaction.user.id),
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            }
            
            created_meeting = await db_client.create_meeting(meeting_data)
            
            # Create initial embed to update as the meeting progresses
            embed = discord.Embed(
                title=f"🔬 Meeting with {agent_name}",
                description=f"**Agenda:** {agenda}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="Starting...", inline=False)
            
            # Send initial response that we'll update
            message = await interaction.followup.send(embed=embed)
            
            # Initialize conversation history
            conversation = []
            
            # Create a transcript record
            transcript_data = []
            
            # Add user's initial message to the conversation
            initial_message = {
                "role": "user",
                "content": f"Agenda: {agenda}" + 
                          (f"\n\nAdditional questions: {agenda_questions}" if agenda_questions else "") +
                          (f"\n\nRules: {rules}" if rules else "")
            }
            conversation.append(initial_message)
            transcript_data.append({
                "id": str(uuid.uuid4()),
                "meetingId": meeting_id,
                "role": "user",
                "agentId": None,
                "agentName": interaction.user.display_name,
                "content": initial_message["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {},
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            })
            
            # Update embed
            embed.add_field(name="Rounds", value=f"0/{rounds} completed", inline=True)
            embed.add_field(name="Critic", value="Enabled" if include_critic else "Disabled", inline=True)
            embed.set_footer(text=f"Meeting ID: {meeting_id}")
            await message.edit(embed=embed)
            
            # Run the conversation for the specified number of rounds
            try:
                for round_num in range(rounds):
                    # Update round info
                    embed.set_field_at(1, name="Rounds", value=f"{round_num}/{rounds} in progress", inline=True)
                    await message.edit(embed=embed)
                    
                    # Get agent response
                    agent_model = target_agent.get("model", "anthropic")
                    agent_specific_model = get_default_model_for_provider(agent_model)
                    
                    # Prepare system prompt for agent
                    system_prompt = get_system_prompt_for_role(
                        target_agent.get("role", "Scientist"),
                        {
                            "name": target_agent["name"],
                            "expertise": target_agent.get("expertise", ""),
                            "goal": target_agent.get("goal", "")
                        }
                    )
                    
                    # Generate response from agent
                    try:
                        agent_response = await llm_client.chat_with_history(
                            provider=agent_model,
                            conversation=conversation,
                            system_prompt=system_prompt,
                            model=agent_specific_model
                        )
                        
                        # Append agent's response to conversation
                        agent_message = {
                            "role": "assistant",
                            "content": agent_response["text"]
                        }
                        conversation.append(agent_message)
                        
                        # Append to transcript
                        transcript_data.append({
                            "id": str(uuid.uuid4()),
                            "meetingId": meeting_id,
                            "role": "assistant",
                            "agentId": target_agent["id"],
                            "agentName": target_agent["name"],
                            "content": agent_response["text"],
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": {"tokens": agent_response.get("usage", {})},
                            "createdAt": datetime.utcnow().isoformat(),
                            "updatedAt": datetime.utcnow().isoformat()
                        })
                        
                        # Create a separate embed for the agent's response
                        agent_embed = discord.Embed(
                            title=f"🔬 {target_agent['name']} (Round {round_num + 1}/{rounds})",
                            description=agent_response["text"][:4000] + ("..." if len(agent_response["text"]) > 4000 else ""),
                            color=discord.Color.blue()
                        )
                        agent_embed.set_footer(text=f"Agent: {target_agent['name']} | Role: {target_agent.get('role', 'Scientist')} | Model: {agent_model}")
                        await interaction.channel.send(embed=agent_embed)
                        
                        # Include critic feedback if requested
                        if include_critic and critic_agent:
                            # Update status
                            embed.set_field_at(0, name="Status", value=f"Generating critic feedback (Round {round_num + 1})", inline=False)
                            await message.edit(embed=embed)
                            
                            # Prepare critic-specific prompt
                            critic_system_prompt = get_system_prompt_for_role(
                                "Critic",
                                {
                                    "name": critic_agent["name"],
                                    "expertise": critic_agent.get("expertise", "Critical analysis"),
                                    "goal": critic_agent.get("goal", "Identify flaws and suggest improvements")
                                }
                            )
                            
                            # Copy conversation and add critic-specific instruction
                            critic_convo = conversation.copy()
                            critic_convo.append({
                                "role": "user",
                                "content": f"Please provide a brief, critical analysis of the response above from {target_agent['name']}. Focus on potential weaknesses, biases, or areas that need more rigorous analysis."
                            })
                            
                            # Generate critic response
                            critic_model = critic_agent.get("model", "anthropic")
                            critic_specific_model = get_default_model_for_provider(critic_model)
                            
                            critic_response = await llm_client.chat_with_history(
                                provider=critic_model,
                                conversation=critic_convo,
                                system_prompt=critic_system_prompt,
                                model=critic_specific_model
                            )
                            
                            # Append critic's feedback to conversation
                            critic_message = {
                                "role": "assistant",
                                "content": f"[CRITIC FEEDBACK]: {critic_response['text']}"
                            }
                            conversation.append(critic_message)
                            
                            # Append to transcript
                            transcript_data.append({
                                "id": str(uuid.uuid4()),
                                "meetingId": meeting_id,
                                "role": "critic",
                                "agentId": critic_agent["id"],
                                "agentName": critic_agent["name"],
                                "content": critic_response["text"],
                                "timestamp": datetime.utcnow().isoformat(),
                                "metadata": {"tokens": critic_response.get("usage", {})},
                                "createdAt": datetime.utcnow().isoformat(),
                                "updatedAt": datetime.utcnow().isoformat()
                            })
                            
                            # Create a separate embed for the critic's response
                            critic_embed = discord.Embed(
                                title=f"🔍 Critic Feedback (Round {round_num + 1}/{rounds})",
                                description=critic_response["text"][:4000] + ("..." if len(critic_response["text"]) > 4000 else ""),
                                color=discord.Color.gold()
                            )
                            critic_embed.set_footer(text=f"Critic: {critic_agent['name']} | Model: {critic_model}")
                            await interaction.channel.send(embed=critic_embed)
                    
                    except Exception as e:
                        logger.error(f"Error generating response for round {round_num + 1}: {str(e)}")
                        await interaction.channel.send(f"⚠️ Error generating response for round {round_num + 1}: {str(e)}")
                        break
                    
                    # If not the last round, add user input as "Let's continue"
                    if round_num < rounds - 1:
                        continue_message = {
                            "role": "user",
                            "content": "Let's continue the discussion. Please provide more insights or develop your previous points further."
                        }
                        conversation.append(continue_message)
                        
                        # Add to transcript
                        transcript_data.append({
                            "id": str(uuid.uuid4()),
                            "meetingId": meeting_id,
                            "role": "user",
                            "agentId": None,
                            "agentName": "System (Auto-continue)",
                            "content": continue_message["content"],
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": {},
                            "createdAt": datetime.utcnow().isoformat(),
                            "updatedAt": datetime.utcnow().isoformat()
                        })
                
                # Save all transcript entries to database
                for entry in transcript_data:
                    await db_client.create_transcript(entry)
                
                # Generate a concise summary
                system_prompt = """You are a skilled research assistant. Your task is to create a very concise summary (2-3 sentences) 
                of the key points and insights from the conversation that just took place. Focus on the most important findings and conclusions."""
                
                summary_conversation = [
                    {"role": "user", "content": f"Here is a research conversation about '{agenda}'. Please provide a concise summary (2-3 sentences):\n\n" + 
                     "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation])}
                ]
                
                summary_response = await llm_client.chat_with_history(
                    provider="anthropic",  # Defaulting to Anthropic for summaries
                    conversation=summary_conversation,
                    system_prompt=system_prompt
                )
                
                # Update meeting record with end time and summary
                await db_client.update_meeting(meeting_id, {
                    "endedAt": datetime.utcnow().isoformat(),
                    "status": "completed",
                    "summary": summary_response["text"],
                    "updatedAt": datetime.utcnow().isoformat()
                })
                
                # Update and finalize the status embed
                embed.clear_fields()
                embed.add_field(name="Status", value="Completed", inline=False)
                embed.add_field(name="Rounds", value=f"{rounds}/{rounds} completed", inline=True)
                embed.add_field(name="Meeting ID", value=meeting_id, inline=True)
                embed.add_field(name="Summary", value=summary_response["text"][:1024], inline=False)
                embed.add_field(
                    name="View Full Transcript", 
                    value="Use `/view_transcript meeting_id:{meeting_id}` to see the complete conversation",
                    inline=False
                )
                embed.set_footer(text=f"Completed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                await message.edit(embed=embed)
                logger.info(f"Individual meeting {meeting_id} with {agent_name} completed")
                
            except Exception as e:
                logger.error(f"Error during individual meeting: {str(e)}")
                embed.set_field_at(0, name="Status", value=f"Error: {str(e)}", inline=False)
                await message.edit(embed=embed)
                
                # Update meeting record with error status
                await db_client.update_meeting(meeting_id, {
                    "endedAt": datetime.utcnow().isoformat(),
                    "status": "error",
                    "updatedAt": datetime.utcnow().isoformat()
                })
        
        except Exception as e:
            logger.error(f"Error setting up individual meeting: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while setting up the meeting: {str(e)}.",
                ephemeral=True
            )

async def setup(bot):
    """Add the cog to the bot - Discord.py extension standard"""
    await bot.add_cog(MeetingCommands(bot)) 