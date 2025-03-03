import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

from db_client import db_client
from models import ModelConfig
from orchestrator import AgentOrchestrator
from llm_client import llm_client

logger = logging.getLogger(__name__)

class QuickstartCommand(commands.Cog):
    """Command for quickly starting a lab session with agents and a meeting."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.orchestrator = AgentOrchestrator(llm_client)
        logger.info("Initialized quickstart command")

    @app_commands.command(
        name="quickstart",
        description="Quickly create a lab session with agents and start a brainstorming session"
    )
    @app_commands.describe(
        topic="The topic or question to discuss",
        agent_count="Number of Scientist agents to create (default: 3)",
        include_critic="Whether to include a Critic agent (default: true)",
        public="Whether the session should be publicly viewable (default: false)"
    )
    async def quickstart(
        self,
        interaction: discord.Interaction,
        topic: str,
        agent_count: Optional[int] = 3,
        include_critic: Optional[bool] = True,
        public: Optional[bool] = False
    ):
        """Quickly start a lab session with agents and begin a discussion."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        user_id = str(interaction.user.id)
        
        try:
            # Check for existing active session and end it
            active_session = await db_client.get_active_session(user_id=user_id)
            if active_session.get("isSuccess") and active_session.get("data"):
                await db_client.end_session(
                    session_id=active_session["data"]["id"]
                )
                logger.info(f"Ended previous active session for user {user_id}")
            
            # Create new session
            session_result = await db_client.create_session(
                user_id=user_id,
                title=topic,
                description=f"Quickstart session on: {topic}",
                is_public=public
            )
            
            if not session_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to create session: {session_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            session_data = session_result.get("data", {})
            session_id = session_data.get("id")
            
            # Create Principal Investigator
            await db_client.create_agent(
                session_id=session_id,
                name=ModelConfig.PRINCIPAL_INVESTIGATOR_ROLE,
                role="Lead",
                goal="Oversee experiment design and coordinate discussion",
                model="openai"
            )
            
            # Create Scientists with varied expertise
            expertise_areas = [
                "Theoretical Analysis",
                "Experimental Design",
                "Data Analysis",
                "Implementation Strategy",
                "Risk Assessment",
                "Innovation Research"
            ]
            
            for i in range(agent_count):
                expertise = expertise_areas[i % len(expertise_areas)]
                await db_client.create_agent(
                    session_id=session_id,
                    name=f"Scientist {i+1}",
                    role=ModelConfig.SCIENTIST_ROLE,
                    expertise=expertise,
                    goal=f"Provide {expertise.lower()} insights",
                    model="openai"
                )
            
            # Create Critic if requested
            if include_critic:
                await db_client.create_agent(
                    session_id=session_id,
                    name="Critic",
                    role=ModelConfig.CRITIC_ROLE,
                    goal="Challenge assumptions and identify potential issues",
                    model="openai"
                )
            
            # Get all created agents
            agents_result = await db_client.get_session_agents(session_id=session_id)
            if not agents_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to retrieve agents: {agents_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            agents = agents_result.get("data", [])
            
            # Create and start the meeting
            meeting_result = await db_client.create_meeting(
                session_id=session_id,
                agenda=topic,
                round_count=3  # Default to 3 rounds for quickstart
            )
            
            if not meeting_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to create meeting: {meeting_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            meeting = meeting_result.get("data", {})
            meeting_id = meeting.get("id")
            
            # Initialize and start the meeting
            await self.orchestrator.initialize_meeting(
                meeting_id=meeting_id,
                session_id=session_id,
                agents=agents,
                agenda=topic,
                round_count=3
            )
            
            # Start the conversation asynchronously
            await self.orchestrator.start_conversation(
                meeting_id=meeting_id,
                interaction=interaction
            )
            
            # Create response embed
            embed = discord.Embed(
                title="Quickstart Complete",
                description=f"Created a new session and started a brainstorming discussion on: {topic}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Session Details",
                value=(
                    f"**ID**: {session_id}\n"
                    f"**Privacy**: {'Public' if public else 'Private'}\n"
                    f"**Agents**: {len(agents)} total\n"
                    f"- 1 Principal Investigator\n"
                    f"- {agent_count} Scientists\n"
                    f"{f'- 1 Critic' if include_critic else ''}"
                ),
                inline=False
            )
            
            embed.add_field(
                name="Meeting",
                value=(
                    f"**ID**: {meeting_id}\n"
                    f"**Rounds**: 3\n"
                    f"**Status**: In Progress"
                ),
                inline=False
            )
            
            embed.add_field(
                name="View Progress",
                value="Use `/lab transcript view meeting_id:{meeting_id}` to view the discussion.",
                inline=False
            )
            
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in quickstart command: {e}")
            await interaction.followup.send(
                "An error occurred while setting up your session. Please try again later.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Add the cog to the bot."""
    await bot.add_cog(QuickstartCommand(bot)) 