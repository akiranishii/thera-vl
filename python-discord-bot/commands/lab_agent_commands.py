import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional, Dict, Any

from db_client import db_client
from models import ModelConfig

logger = logging.getLogger(__name__)

class LabAgentCommands(commands.Cog):
    """Commands for managing lab agents"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Find the existing lab group or create a new one if it doesn't exist
        self.lab_group = None
        for command in bot.tree.get_commands():
            if command.name == "lab" and isinstance(command, app_commands.Group):
                self.lab_group = command
                break
                
        if not self.lab_group:
            # Create a command group for lab commands if it doesn't exist
            self.lab_group = app_commands.Group(
                name="lab",
                description="Lab management commands",
                guild_ids=None  # None means global commands
            )
            bot.tree.add_command(self.lab_group)
            logger.info("Created new lab command group")
        else:
            logger.info("Using existing lab command group")
        
        # Add agent commands to the lab group
        self.lab_group.add_command(app_commands.Command(
            name="agent_create",
            description="Create a new AI agent in the current lab session",
            callback=self.create_agent_callback,
            extras={"cog": self}
        ))
        
        self.lab_group.add_command(app_commands.Command(
            name="agent_update",
            description="Update an existing agent in the current lab session",
            callback=self.update_agent_callback,
            extras={"cog": self}
        ))
        
        self.lab_group.add_command(app_commands.Command(
            name="agent_delete",
            description="Delete an agent from the current lab session",
            callback=self.delete_agent_callback,
            extras={"cog": self}
        ))
        
        self.lab_group.add_command(app_commands.Command(
            name="agent_list",
            description="List all agents in the current lab session",
            callback=self.list_agents_callback,
            extras={"cog": self}
        ))
        
        logger.info("Registered lab agent commands")

    @app_commands.describe(
        agent_name="Name of the agent to create",
        expertise="Agent's area of expertise (e.g., 'Structural biology')",
        goal="Agent's main objective (e.g., 'Propose novel protein scaffolds')",
        role="Agent's functional role in the team",
        model="LLM model to use for the agent"
    )
    @app_commands.choices(role=[
        app_commands.Choice(name="Principal Investigator", value=ModelConfig.PRINCIPAL_INVESTIGATOR_ROLE),
        app_commands.Choice(name="Scientist", value=ModelConfig.SCIENTIST_ROLE),
        app_commands.Choice(name="Critic", value=ModelConfig.CRITIC_ROLE),
    ])
    @app_commands.choices(model=[
        app_commands.Choice(name="OpenAI", value="openai"),
        app_commands.Choice(name="Anthropic", value="anthropic"),
        app_commands.Choice(name="Mistral", value="mistral"),
    ])
    async def create_agent_callback(self, interaction: discord.Interaction, agent_name: str, expertise: Optional[str] = None, goal: Optional[str] = None, role: Optional[app_commands.Choice[str]] = None, model: Optional[app_commands.Choice[str]] = None):
        """Callback for the create_agent command."""
        role_value = role.value if role else None
        model_value = model.value if model else "openai"
        await self.create_agent(interaction, agent_name, expertise, goal, role_value, model_value)
        
    @app_commands.describe(
        agent_name="Name of the agent to update",
        expertise="Agent's area of expertise (e.g., 'Structural biology')",
        goal="Agent's main objective (e.g., 'Propose novel protein scaffolds')",
        role="Agent's functional role in the team",
        model="LLM model to use for the agent"
    )
    @app_commands.choices(role=[
        app_commands.Choice(name="Principal Investigator", value=ModelConfig.PRINCIPAL_INVESTIGATOR_ROLE),
        app_commands.Choice(name="Scientist", value=ModelConfig.SCIENTIST_ROLE),
        app_commands.Choice(name="Critic", value=ModelConfig.CRITIC_ROLE),
        app_commands.Choice(name="Tool Agent", value="Tool Agent"),
    ])
    @app_commands.choices(model=[
        app_commands.Choice(name="OpenAI", value="openai"),
        app_commands.Choice(name="Anthropic", value="anthropic"),
        app_commands.Choice(name="Mistral", value="mistral"),
    ])
    async def update_agent_callback(self, interaction: discord.Interaction, agent_name: str, expertise: Optional[str] = None, goal: Optional[str] = None, role: Optional[app_commands.Choice[str]] = None, model: Optional[app_commands.Choice[str]] = None):
        """Callback for the update_agent command."""
        role_value = role.value if role else None
        model_value = model.value if model else None
        await self.update_agent(interaction, agent_name, expertise, goal, role_value, model_value)
        
    async def delete_agent_callback(self, interaction: discord.Interaction, agent_name: str):
        """Callback for the delete_agent command."""
        await self.delete_agent(interaction, agent_name)
        
    async def list_agents_callback(self, interaction: discord.Interaction):
        """Callback for the list_agents command."""
        await self.list_agents(interaction)

    async def create_agent(
        self,
        interaction: discord.Interaction,
        agent_name: str,
        expertise: Optional[str] = None,
        goal: Optional[str] = None,
        role: Optional[str] = None,
        model: Optional[str] = "openai"
    ):
        """Create a new AI agent in the current lab session."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        user_id = str(interaction.user.id)
        
        try:
            # Get active session
            session_result = await db_client.get_active_session(user_id=user_id)
            
            if not session_result.get("isSuccess") or not session_result.get("data"):
                await interaction.followup.send(
                    "You don't have an active session. Use `/lab start` to create one.",
                    ephemeral=True
                )
                return
                
            session_data = session_result.get("data", {})
            session_id = session_data.get("id")
            
            # Use default role if none provided
            if not role:
                role = ModelConfig.SCIENTIST_ROLE
            
            # Create the agent
            agent_result = await db_client.create_agent(
                session_id=session_id,
                user_id=user_id,
                name=agent_name,
                expertise=expertise,
                goal=goal,
                role=role,
                model=model
            )
            
            if not agent_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to create agent: {agent_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
                
            agent_data = agent_result.get("data", {})
            
            # Create response embed
            embed = discord.Embed(
                title="Agent Created",
                description=f"Agent '{agent_name}' has been created.",
                color=discord.Color.green()
            )
            
            # Add agent details
            field_value = []
            
            # Add role with description
            if role:
                role_display = role
                role_description = ""
                
                # Add note for predefined roles
                if role == ModelConfig.PRINCIPAL_INVESTIGATOR_ROLE:
                    role_description = " - Team leader who guides the research direction"
                elif role == ModelConfig.SCIENTIST_ROLE:
                    role_description = " - Domain expert who contributes specialized knowledge"
                elif role == ModelConfig.CRITIC_ROLE:
                    role_description = " - Critical reviewer who ensures scientific rigor"
                elif role == "Tool Agent":
                    role_description = " - Agent that retrieves information from external sources"
                    
                field_value.append(f"**Role**: {role_display}{role_description}")
                
            if expertise:
                field_value.append(f"**Expertise**: {expertise}")
            if goal:
                field_value.append(f"**Goal**: {goal}")
            if model:
                model_display = model
                if model == "openai":
                    model_display = "OpenAI"
                elif model == "anthropic":
                    model_display = "Anthropic"
                elif model == "mistral":
                    model_display = "Mistral"
                field_value.append(f"**Model**: {model_display}")
                
            if field_value:
                embed.add_field(
                    name="Agent Details",
                    value="\n".join(field_value),
                    inline=False
                )
            
            embed.add_field(
                name="ID",
                value=agent_data.get("id", "Unknown"),
                inline=False
            )
            
            # Add tips for usage
            embed.add_field(
                name="Tips",
                value=(
                    f"• Use this agent in team meetings with `/lab team_meeting`\n"
                    f"• Update with `/lab agent_update agent_name:\"{agent_name}\"`\n"
                    f"• Delete with `/lab agent_delete agent_name:\"{agent_name}\"`"
                ),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in create_agent command: {e}")
            await interaction.followup.send(
                "An error occurred while creating the agent. Please try again later.",
                ephemeral=True
            )

    async def update_agent(
        self,
        interaction: discord.Interaction,
        agent_name: str,
        expertise: Optional[str] = None,
        goal: Optional[str] = None,
        role: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Update an existing agent in the current lab session."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        user_id = str(interaction.user.id)
        
        try:
            # Get active session
            session_result = await db_client.get_active_session(user_id=user_id)
            
            if not session_result.get("isSuccess") or not session_result.get("data"):
                await interaction.followup.send(
                    "You don't have an active session. Use `/lab start` to create one.",
                    ephemeral=True
                )
                return
                
            session_data = session_result.get("data", {})
            session_id = session_data.get("id")
            
            # Build updates object
            updates = {}
            if expertise is not None:
                updates["expertise"] = expertise
            if goal is not None:
                updates["description"] = goal  # Map goal to description for the database
            if role is not None:
                updates["role"] = role
            if model is not None:
                updates["model"] = model
            
            # First, get the agent's ID by name
            lookup_result = await db_client.get_agent_by_name(
                session_id=session_id,
                agent_name=agent_name
            )
            
            if not lookup_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Could not find agent '{agent_name}': {lookup_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
                
            agent_id = lookup_result.get("data", {}).get("id")
            if not agent_id:
                await interaction.followup.send(
                    f"Invalid agent data retrieved for '{agent_name}'",
                    ephemeral=True
                )
                return
                
            # Now update the agent using the updates dictionary
            update_result = await db_client.update_agent(
                agent_id=agent_id,
                updates=updates
            )
            
            if not update_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to update agent: {update_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            agent_data = update_result.get("data", {})
            
            # Create response embed
            embed = discord.Embed(
                title="Agent Updated",
                description=f"Agent '{agent_name}' has been updated.",
                color=discord.Color.blue()
            )
            
            # Add what was updated
            updated_fields = []
            if expertise is not None:
                updated_fields.append(f"**Expertise**: {expertise}")
            if goal is not None:
                updated_fields.append(f"**Goal**: {goal}")
            if role is not None:
                role_display = role
                role_description = ""
                
                # Add note for predefined roles
                if role == ModelConfig.PRINCIPAL_INVESTIGATOR_ROLE:
                    role_description = " - Team leader who guides the research direction"
                elif role == ModelConfig.SCIENTIST_ROLE:
                    role_description = " - Domain expert who contributes specialized knowledge"
                elif role == ModelConfig.CRITIC_ROLE:
                    role_description = " - Critical reviewer who ensures scientific rigor"
                elif role == "Tool Agent":
                    role_description = " - Agent that retrieves information from external sources"
                    
                updated_fields.append(f"**Role**: {role_display}{role_description}")
            if model is not None:
                model_display = model
                if model == "openai":
                    model_display = "OpenAI"
                elif model == "anthropic":
                    model_display = "Anthropic"
                elif model == "mistral":
                    model_display = "Mistral"
                updated_fields.append(f"**Model**: {model_display}")
                
            if updated_fields:
                embed.add_field(
                    name="Updated Fields",
                    value="\n".join(updated_fields),
                    inline=False
                )
            
            embed.add_field(
                name="ID",
                value=agent_data.get("id", "Unknown"),
                inline=False
            )
            
            # Add tips for using this agent
            embed.add_field(
                name="Next Steps",
                value=(
                    f"• Use this agent in team meetings with `/lab team_meeting`\n"
                    f"• List all agents with `/lab agent_list`"
                ),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in update_agent command: {e}")
            await interaction.followup.send(
                "An error occurred while updating the agent. Please try again later.",
                ephemeral=True
            )

    async def delete_agent(
        self,
        interaction: discord.Interaction,
        agent_name: str
    ):
        """Delete an agent from the current lab session."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        user_id = str(interaction.user.id)
        
        try:
            # Get active session
            session_result = await db_client.get_active_session(user_id=user_id)
            
            if not session_result.get("isSuccess") or not session_result.get("data"):
                await interaction.followup.send(
                    "You don't have an active session. Use `/lab start` to create one.",
                    ephemeral=True
                )
                return
            
            session_data = session_result.get("data", {})
            session_id = session_data.get("id")
            
            # First, get the agent's ID by name
            lookup_result = await db_client.get_agent_by_name(
                session_id=session_id,
                agent_name=agent_name
            )
            
            if not lookup_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Could not find agent '{agent_name}': {lookup_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            agent_id = lookup_result.get("data", {}).get("id")
            if not agent_id:
                await interaction.followup.send(
                    f"Invalid agent data retrieved for '{agent_name}'",
                    ephemeral=True
                )
                return
                
            # Delete the agent using its ID
            delete_result = await db_client.delete_agent(
                agent_id=agent_id
            )
            
            if not delete_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to delete agent: {delete_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            # Create response embed
            embed = discord.Embed(
                title="Agent Deleted",
                description=f"Agent '{agent_name}' has been deleted.",
                color=discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in delete_agent command: {e}")
            await interaction.followup.send(
                "An error occurred while deleting the agent. Please try again later.",
                ephemeral=True
            )

    async def list_agents(
        self,
        interaction: discord.Interaction
    ):
        """List all agents in the current lab session."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        user_id = str(interaction.user.id)
        
        try:
            # Get active session
            session_result = await db_client.get_active_session(user_id=user_id)
            
            if not session_result.get("isSuccess") or not session_result.get("data"):
                await interaction.followup.send(
                    "You don't have an active session. Use `/lab start` to create one.",
                    ephemeral=True
                )
                return
            
            session_data = session_result.get("data", {})
            session_id = session_data.get("id")
            
            # Get all created agents
            agents_result = await db_client.get_session_agents(
                session_id=session_id,
                user_id=str(interaction.user.id)
            )
            
            if not agents_result.get("isSuccess"):
                await interaction.followup.send(
                    f"Failed to fetch agents: {agents_result.get('message', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            agents = agents_result.get("data", [])
            
            if not agents:
                await interaction.followup.send(
                    "No agents found in the current session. Use `/lab agent create` to add one.",
                    ephemeral=True
                )
                return
            
            # Create response embed
            embed = discord.Embed(
                title="Lab Session Agents",
                description=f"Agents in session '{session_data.get('title')}':",
                color=discord.Color.blue()
            )
            
            for agent in agents:
                field_value = []
                if agent.get("expertise"):
                    field_value.append(f"Expertise: {agent['expertise']}")
                if agent.get("goal"):
                    field_value.append(f"Goal: {agent['goal']}")
                if agent.get("role"):
                    field_value.append(f"Role: {agent['role']}")
                if agent.get("model"):
                    field_value.append(f"Model: {agent['model']}")
                
                embed.add_field(
                    name=agent["name"],
                    value="\n".join(field_value) if field_value else "No additional details",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in list_agents command: {e}")
            await interaction.followup.send(
                "An error occurred while fetching the agents. Please try again later.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Add the cog to the bot."""
    await bot.add_cog(LabAgentCommands(bot)) 