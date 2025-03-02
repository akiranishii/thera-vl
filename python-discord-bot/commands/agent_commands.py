"""
Agent management commands for the Discord bot.
Includes commands for creating and configuring research AI agents.
"""

import os
import uuid
import discord
import logging
import asyncio
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Literal

from config import Config
from db_client import SupabaseClient
from commands.session_commands import SessionCommands

logger = logging.getLogger('agent_commands')

# Create Supabase client
db_client = SupabaseClient()

# Predefined role options
AGENT_MODELS = Literal["openai", "anthropic", "mistral"]
AGENT_ROLES = Literal["Principal Investigator", "Scientist", "Critic"]

class AgentCommands(commands.Cog):
    """Commands for managing AI research agents"""

    def __init__(self, bot):
        self.bot = bot
        self.session_cog = None
        
    async def cog_load(self):
        """Find the session commands cog to access active sessions"""
        self.session_cog = self.bot.get_cog("SessionCommands")
        if not self.session_cog:
            logger.error("SessionCommands cog not found. Agent commands may not work properly.")

    @app_commands.command(
        name="create_agent",
        description="Create or update an AI research agent"
    )
    @app_commands.describe(
        agent_name="Name of the agent (e.g., Biologist, Principal Investigator)",
        expertise="Domain expertise of the agent (e.g., Structural Biology)",
        goal="The agent's overarching objective",
        role="The agent's functional role in conversations",
        model="The LLM model to use for this agent"
    )
    @app_commands.choices(
        model=[
            app_commands.Choice(name="OpenAI (GPT-4)", value="openai"),
            app_commands.Choice(name="Anthropic (Claude)", value="anthropic"),
            app_commands.Choice(name="Mistral AI", value="mistral")
        ],
        role=[
            app_commands.Choice(name="Principal Investigator", value="Principal Investigator"),
            app_commands.Choice(name="Scientist", value="Scientist"),
            app_commands.Choice(name="Critic", value="Critic")
        ]
    )
    async def create_agent(
        self, 
        interaction: discord.Interaction, 
        agent_name: str,
        expertise: Optional[str] = None,
        goal: Optional[str] = None,
        role: Optional[str] = None,
        model: Optional[str] = "openai"
    ):
        """
        Create or update an AI research agent for scientific collaboration.
        
        Args:
            interaction: The Discord interaction
            agent_name: Name of the agent (e.g., Biologist, Principal Investigator)
            expertise: Domain expertise of the agent (e.g., Structural Biology)
            goal: The agent's overarching objective
            role: The agent's functional role in conversations
            model: The LLM model to use for this agent
        """
        # Verify that a session is active in this channel
        channel_id = str(interaction.channel_id)
        
        if not self.session_cog:
            await interaction.response.send_message(
                "⚠️ Could not access session information. Please try again later.",
                ephemeral=True
            )
            return
            
        if channel_id not in self.session_cog.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active research session found in this channel. Start one with `/startlab` first.",
                ephemeral=True
            )
            return
        
        active_session = self.session_cog.active_sessions[channel_id]
        session_id = active_session["id"]
        
        # Validate model choice
        if model not in ["openai", "anthropic", "mistral"]:
            model = "openai"  # Default to OpenAI if an invalid value is provided
        
        try:
            # Create agent data structure
            agent_data = {
                "id": str(uuid.uuid4()),
                "sessionId": session_id,
                "name": agent_name,
                "expertise": expertise if expertise else "",
                "goal": goal if goal else "",
                "role": role if role else "",
                "model": model,
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
                "createdBy": str(interaction.user.id)
            }
            
            # Check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. Please try again later.",
                    ephemeral=True
                )
                return
            
            # Create agent in database
            created_agent = await db_client.create_agent(agent_data)
            
            # If we have an agents list in the active session, add this agent to it
            if "agents" not in active_session:
                active_session["agents"] = []
                
            active_session["agents"].append({
                "id": created_agent["id"],
                "name": created_agent["name"],
                "role": created_agent["role"] if created_agent["role"] else "Not specified",
                "model": created_agent["model"]
            })
            
            # Create response embed
            embed = discord.Embed(
                title="🧠 Research Agent Created",
                description=f"**{agent_name}**",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Role", value=role if role else "Not specified", inline=True)
            embed.add_field(name="Model", value=model.capitalize(), inline=True)
            
            if expertise:
                embed.add_field(name="Expertise", value=expertise, inline=False)
            if goal:
                embed.add_field(name="Goal", value=goal, inline=False)
                
            embed.add_field(
                name="Commands", 
                value="• `/individual_meeting` - Start a 1:1 meeting with this agent\n• `/brainstorm` - Start a multi-agent brainstorming session",
                inline=False
            )
            
            embed.set_footer(text=f"Agent ID: {created_agent['id']}")
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"Agent {created_agent['id']} created by {interaction.user.name} (ID: {interaction.user.id})")
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ Failed to create agent: {str(e)}. Please try again later.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="list_agents",
        description="List all agents in the current research session"
    )
    async def list_agents(self, interaction: discord.Interaction):
        """
        List all agents created for the current research session.
        
        Args:
            interaction: The Discord interaction
        """
        # Verify that a session is active in this channel
        channel_id = str(interaction.channel_id)
        
        if not self.session_cog:
            await interaction.response.send_message(
                "⚠️ Could not access session information. Please try again later.",
                ephemeral=True
            )
            return
            
        if channel_id not in self.session_cog.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active research session found in this channel. Start one with `/startlab` first.",
                ephemeral=True
            )
            return
        
        active_session = self.session_cog.active_sessions[channel_id]
        session_id = active_session["id"]
        
        try:
            # Check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. Please try again later.",
                    ephemeral=True
                )
                return
            
            # Get agents from database
            agents = await db_client.get_agents({"sessionId": session_id})
            
            if not agents:
                await interaction.response.send_message(
                    "No agents found in this research session. Create one with `/create_agent`.",
                    ephemeral=True
                )
                return
            
            # Create response embed
            embed = discord.Embed(
                title="🧪 Research Agents",
                description=f"Found {len(agents)} agent(s) in this research session:",
                color=discord.Color.blue()
            )
            
            for agent in agents:
                embed.add_field(
                    name=f"{agent['name']}",
                    value=f"Role: {agent['role'] if agent['role'] else 'Not specified'}\n"
                          f"Model: {agent['model'].capitalize()}\n"
                          f"Expertise: {agent['expertise'] if agent['expertise'] else 'Not specified'}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ An error occurred while listing agents: {str(e)}.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="delete_agent",
        description="Delete an agent from the current research session"
    )
    @app_commands.describe(
        agent_name="Name of the agent to delete"
    )
    async def delete_agent(self, interaction: discord.Interaction, agent_name: str):
        """
        Delete an agent from the current research session.
        
        Args:
            interaction: The Discord interaction
            agent_name: Name of the agent to delete
        """
        # Verify that a session is active in this channel
        channel_id = str(interaction.channel_id)
        
        if not self.session_cog:
            await interaction.response.send_message(
                "⚠️ Could not access session information. Please try again later.",
                ephemeral=True
            )
            return
            
        if channel_id not in self.session_cog.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active research session found in this channel. Start one with `/startlab` first.",
                ephemeral=True
            )
            return
        
        active_session = self.session_cog.active_sessions[channel_id]
        session_id = active_session["id"]
        
        try:
            # Check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.response.send_message(
                    "⚠️ Failed to connect to the database. Please try again later.",
                    ephemeral=True
                )
                return
            
            # Find agent by name in this session
            agents = await db_client.get_agents({"sessionId": session_id})
            matching_agent = next((a for a in agents if a["name"].lower() == agent_name.lower()), None)
            
            if not matching_agent:
                await interaction.response.send_message(
                    f"⚠️ No agent named '{agent_name}' found in this session.",
                    ephemeral=True
                )
                return
            
            # Delete the agent
            agent_id = matching_agent["id"]
            await db_client.delete_agent(agent_id)
            
            # Update local cache
            if "agents" in active_session:
                active_session["agents"] = [a for a in active_session["agents"] if a["name"].lower() != agent_name.lower()]
            
            await interaction.response.send_message(
                f"✅ Agent '{agent_name}' has been deleted from this research session.",
                ephemeral=False
            )
            logger.info(f"Agent {agent_id} deleted by {interaction.user.name} (ID: {interaction.user.id})")
            
        except Exception as e:
            logger.error(f"Error deleting agent: {str(e)}")
            await interaction.response.send_message(
                f"⚠️ An error occurred while deleting the agent: {str(e)}.",
                ephemeral=True
            )

    @app_commands.command(
        name="generate_agents",
        description="Auto-generate a set of research agents based on a topic"
    )
    @app_commands.describe(
        topic="Research topic to generate agents for",
        count="Number of scientists to generate (in addition to 1 PI and 1 Critic)"
    )
    async def generate_agents(
        self, 
        interaction: discord.Interaction, 
        topic: str,
        count: Optional[int] = 3
    ):
        """
        Auto-generate a set of research agents with diverse expertise based on a topic.
        
        Args:
            interaction: The Discord interaction
            topic: Research topic to generate agents for
            count: Number of scientists to generate (in addition to 1 PI and 1 Critic)
        """
        # Verify that a session is active in this channel
        channel_id = str(interaction.channel_id)
        
        if not self.session_cog:
            await interaction.response.send_message(
                "⚠️ Could not access session information. Please try again later.",
                ephemeral=True
            )
            return
            
        if channel_id not in self.session_cog.active_sessions:
            await interaction.response.send_message(
                "⚠️ No active research session found in this channel. Start one with `/startlab` first.",
                ephemeral=True
            )
            return
        
        active_session = self.session_cog.active_sessions[channel_id]
        session_id = active_session["id"]
        
        # Validate count
        if count < 1:
            count = 3  # Default to 3 scientists
        elif count > 5:
            count = 5  # Cap at 5 to avoid creating too many
        
        try:
            # First, send a deferred response while we process
            await interaction.response.defer(thinking=True)
            
            # In a real implementation, this would call the LLM to generate diverse agent profiles
            # For now, we'll create predetermined agents with slight variations
            
            # Create the Principal Investigator
            pi_agent = {
                "id": str(uuid.uuid4()),
                "sessionId": session_id,
                "name": "Principal Investigator",
                "expertise": f"Research leadership in {topic}",
                "goal": f"Lead the research team to discover new insights about {topic}",
                "role": "Principal Investigator",
                "model": "openai",  # Default to OpenAI for PI
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
                "createdBy": str(interaction.user.id)
            }
            
            # Create the Critic
            critic_agent = {
                "id": str(uuid.uuid4()),
                "sessionId": session_id,
                "name": "Scientific Critic",
                "expertise": "Research methodology and critical analysis",
                "goal": f"Ensure scientific rigor in all discussions about {topic}",
                "role": "Critic",
                "model": "anthropic",  # Default to Anthropic for Critic
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat(),
                "createdBy": str(interaction.user.id)
            }
            
            # Create scientist agents
            scientist_agents = []
            expertise_areas = [
                f"Theoretical aspects of {topic}",
                f"Experimental methods in {topic}",
                f"Data analysis for {topic}",
                f"Interdisciplinary applications of {topic}",
                f"Historical context of {topic}"
            ]
            
            for i in range(min(count, len(expertise_areas))):
                scientist_agents.append({
                    "id": str(uuid.uuid4()),
                    "sessionId": session_id,
                    "name": f"Scientist {i+1}",
                    "expertise": expertise_areas[i],
                    "goal": f"Contribute specialized knowledge about {expertise_areas[i]}",
                    "role": "Scientist",
                    "model": "mistral" if i % 2 == 0 else "openai",  # Alternate between models
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat(),
                    "createdBy": str(interaction.user.id)
                })
            
            # Check DB connection
            connection_ok = await db_client.check_connection()
            if not connection_ok:
                await interaction.followup.send(
                    "⚠️ Failed to connect to the database. Please try again later.",
                    ephemeral=True
                )
                return
            
            # Create all agents in the database
            created_agents = []
            
            # Create PI
            created_pi = await db_client.create_agent(pi_agent)
            created_agents.append(created_pi)
            
            # Create Critic
            created_critic = await db_client.create_agent(critic_agent)
            created_agents.append(created_critic)
            
            # Create Scientists
            for agent_data in scientist_agents:
                created_scientist = await db_client.create_agent(agent_data)
                created_agents.append(created_scientist)
            
            # Update the session's local cache of agents
            if "agents" not in active_session:
                active_session["agents"] = []
                
            for agent in created_agents:
                active_session["agents"].append({
                    "id": agent["id"],
                    "name": agent["name"],
                    "role": agent["role"],
                    "model": agent["model"]
                })
            
            # Create response embed
            embed = discord.Embed(
                title="🔬 Research Team Generated",
                description=f"Created {len(created_agents)} agents specialized in {topic}:",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Team Composition", value=f"1 Principal Investigator\n1 Scientific Critic\n{count} Specialized Scientists", inline=False)
            
            for agent in created_agents:
                embed.add_field(
                    name=f"{agent['name']} ({agent['role']})",
                    value=f"Expertise: {agent['expertise']}\nModel: {agent['model'].capitalize()}",
                    inline=True
                )
            
            embed.add_field(
                name="Next Steps", 
                value="• Use `/brainstorm` to start a multi-agent discussion\n• Use `/individual_meeting` to chat with a specific agent\n• Use `/list_agents` to see all your agents",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Generated {len(created_agents)} agents for session {session_id} based on topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error generating agents: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while generating agents: {str(e)}.",
                ephemeral=True
            )

async def setup(bot):
    """Add the cog to the bot - Discord.py extension standard"""
    await bot.add_cog(AgentCommands(bot)) 