"""
Help command for the Discord bot.
Displays information about all available commands and their usage.
"""

import discord
import logging
from discord import app_commands
from discord.ext import commands
from typing import Optional, List, Dict, Any

# Set up logging
logger = logging.getLogger('help')

class HelpCommand(commands.Cog):
    """Commands for providing help and documentation"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(
        name="help",
        description="Display help information about Thera and available commands"
    )
    @app_commands.describe(
        command="Optional: Get detailed help for a specific command",
        category="Optional: Filter help by category (session, agent, meeting, brainstorm, transcript)"
    )
    async def help(
        self,
        interaction: discord.Interaction,
        command: Optional[str] = None,
        category: Optional[str] = None
    ):
        """
        Display help information about Thera and available commands
        
        Args:
            interaction: The Discord interaction
            command: Optional specific command to get help for
            category: Optional category to filter help by
        """
        await interaction.response.defer(thinking=True)
        
        try:
            # If a specific command was requested
            if command:
                await self._show_command_help(interaction, command)
                return
                
            # If a category was specified
            if category:
                await self._show_category_help(interaction, category)
                return
                
            # Otherwise show the main help overview
            await self._show_main_help(interaction)
            
        except Exception as e:
            logger.error(f"Error displaying help: {str(e)}")
            await interaction.followup.send(
                f"⚠️ An error occurred while displaying help: {str(e)}.",
                ephemeral=True
            )
    
    async def _show_main_help(self, interaction: discord.Interaction):
        """Show the main help overview with all command categories"""
        
        # Create the main embed
        embed = discord.Embed(
            title="🧠 Thera - AI Research Assistant",
            description=(
                "Welcome to Thera, your AI research assistant! Thera helps you organize "
                "research sessions, manage specialized AI agents, conduct brainstorming "
                "sessions, and maintain a record of your research activities."
            ),
            color=discord.Color.blue()
        )
        
        # Add command categories
        embed.add_field(
            name="📋 Session Commands",
            value=(
                "`/new_session` - Create a new research session\n"
                "`/show_sessions` - List active research sessions\n"
                "`/end_session` - End an active research session"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧬 Agent Commands",
            value=(
                "`/create_agent` - Create a new AI research agent\n"
                "`/list_agents` - List available research agents\n"
                "`/edit_agent` - Edit an existing agent\n"
                "`/delete_agent` - Delete an agent"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔍 Meeting Commands",
            value=(
                "`/meeting` - Start a one-on-one meeting with an agent\n"
                "`/end_meeting` - End an active meeting"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧠 Brainstorming Commands",
            value=(
                "`/brainstorm` - Conduct a multi-agent brainstorming session\n"
                "`/cancel_brainstorm` - Cancel an active brainstorming session\n"
                "`/compare_brainstorms` - Compare multiple brainstorming sessions"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📝 Transcript Commands",
            value=(
                "`/view_transcript` - View a meeting or brainstorming transcript\n"
                "`/list_transcripts` - List available transcripts"
            ),
            inline=False
        )
        
        # Add footer with instructions for detailed help
        embed.set_footer(text="For detailed help on a specific command, use /help command:command_name")
        
        await interaction.followup.send(embed=embed)
    
    async def _show_category_help(self, interaction: discord.Interaction, category: str):
        """Show detailed help for a specific category of commands"""
        
        category = category.lower()
        
        # Define categories and their commands
        categories = {
            "session": {
                "title": "📋 Session Commands",
                "description": "Commands for managing research sessions",
                "commands": [
                    {
                        "name": "new_session",
                        "description": "Create a new research session",
                        "usage": "/new_session title:\"Session Title\" [description:\"Optional description\"]",
                        "details": "Creates a new research context for organizing agents, meetings, and brainstorming sessions."
                    },
                    {
                        "name": "show_sessions",
                        "description": "List active research sessions",
                        "usage": "/show_sessions [limit:10]",
                        "details": "Displays a list of active research sessions, including their ID, title, and creation date."
                    },
                    {
                        "name": "end_session",
                        "description": "End an active research session",
                        "usage": "/end_session session_id:\"session_id\"",
                        "details": "Marks a research session as completed. This doesn't delete any data but closes the session."
                    }
                ]
            },
            "agent": {
                "title": "🧬 Agent Commands",
                "description": "Commands for managing AI research agents",
                "commands": [
                    {
                        "name": "create_agent",
                        "description": "Create a new AI research agent",
                        "usage": "/create_agent name:\"Agent Name\" role:\"Role\" [expertise:\"Expertise areas\"] [goal:\"Agent goal\"] [provider:\"LLM provider\"]",
                        "details": "Creates a specialized AI research agent with specific expertise and goals."
                    },
                    {
                        "name": "list_agents",
                        "description": "List available research agents",
                        "usage": "/list_agents [role:\"Optional role filter\"] [session_id:\"Optional session ID\"]",
                        "details": "Shows all available agents, optionally filtered by role or session."
                    },
                    {
                        "name": "edit_agent",
                        "description": "Edit an existing agent",
                        "usage": "/edit_agent agent_id:\"agent_id\" [name:\"New name\"] [role:\"New role\"] [expertise:\"New expertise\"] [goal:\"New goal\"] [provider:\"New LLM provider\"]",
                        "details": "Updates the properties of an existing agent."
                    },
                    {
                        "name": "delete_agent",
                        "description": "Delete an agent",
                        "usage": "/delete_agent agent_id:\"agent_id\"",
                        "details": "Permanently removes an agent from the system."
                    }
                ]
            },
            "meeting": {
                "title": "🔍 Meeting Commands",
                "description": "Commands for conducting one-on-one meetings with agents",
                "commands": [
                    {
                        "name": "meeting",
                        "description": "Start a one-on-one meeting with an agent",
                        "usage": "/meeting agent_id:\"agent_id\" agenda:\"Meeting agenda\" [session_id:\"Optional session ID\"] [context:\"Additional context\"]",
                        "details": "Initiates a conversation with a specific research agent about a defined topic."
                    },
                    {
                        "name": "end_meeting",
                        "description": "End an active meeting",
                        "usage": "/end_meeting [meeting_id:\"Optional meeting ID\"]",
                        "details": "Concludes an active meeting and generates a summary of the discussion."
                    }
                ]
            },
            "brainstorm": {
                "title": "🧠 Brainstorming Commands",
                "description": "Commands for multi-agent brainstorming sessions",
                "commands": [
                    {
                        "name": "brainstorm",
                        "description": "Conduct a multi-agent brainstorming session",
                        "usage": "/brainstorm agenda:\"Research topic\" [agent_count:3] [rounds:3] [include_critic:true] [agent_list:\"Agent1,Agent2\"] [agenda_questions:\"Additional questions\"] [rules:\"Session rules\"] [parallel_meetings:1]",
                        "details": "Orchestrates a discussion between multiple AI agents on a research topic, with optional critic feedback."
                    },
                    {
                        "name": "cancel_brainstorm",
                        "description": "Cancel an active brainstorming session",
                        "usage": "/cancel_brainstorm",
                        "details": "Stops any active brainstorming sessions in the current channel."
                    },
                    {
                        "name": "compare_brainstorms",
                        "description": "Compare multiple brainstorming sessions",
                        "usage": "/compare_brainstorms meeting_ids:\"id1,id2,id3\"",
                        "details": "Analyzes and compares the results of multiple brainstorming sessions on the same or related topics."
                    }
                ]
            },
            "transcript": {
                "title": "📝 Transcript Commands",
                "description": "Commands for viewing and managing transcripts",
                "commands": [
                    {
                        "name": "view_transcript",
                        "description": "View a meeting or brainstorming transcript",
                        "usage": "/view_transcript meeting_id:\"meeting_id\" [format:\"full\"] [export:false]",
                        "details": "Displays the transcript of a completed meeting or brainstorming session. Formats include 'full' or 'summary'."
                    },
                    {
                        "name": "list_transcripts",
                        "description": "List available transcripts",
                        "usage": "/list_transcripts [session_id:\"Optional session ID\"] [limit:10]",
                        "details": "Shows a list of available transcripts, optionally filtered by session."
                    }
                ]
            }
        }
        
        # Check if the category exists
        if category not in categories:
            await interaction.followup.send(
                f"⚠️ Unknown category: '{category}'. Available categories are: session, agent, meeting, brainstorm, transcript",
                ephemeral=True
            )
            return
            
        # Get the category info
        cat_info = categories[category]
        
        # Create the category embed
        embed = discord.Embed(
            title=cat_info["title"],
            description=cat_info["description"],
            color=discord.Color.blue()
        )
        
        # Add each command
        for cmd in cat_info["commands"]:
            embed.add_field(
                name=f"/{cmd['name']}",
                value=f"**Description:** {cmd['description']}\n**Usage:** `{cmd['usage']}`\n**Details:** {cmd['details']}",
                inline=False
            )
            
        # Add footer
        embed.set_footer(text=f"For detailed help on a specific command, use /help command:command_name")
        
        await interaction.followup.send(embed=embed)
    
    async def _show_command_help(self, interaction: discord.Interaction, command_name: str):
        """Show detailed help for a specific command"""
        
        # Remove leading slash if present
        if command_name.startswith('/'):
            command_name = command_name[1:]
            
        # Define all commands with their detailed help
        commands = {
            # Session commands
            "new_session": {
                "category": "Session",
                "description": "Create a new research session",
                "usage": "/new_session title:\"Session Title\" [description:\"Optional description\"]",
                "parameters": [
                    {"name": "title", "description": "Title of the research session", "required": True},
                    {"name": "description", "description": "Optional detailed description of the session's purpose", "required": False}
                ],
                "examples": [
                    "/new_session title:\"Gene Editing Research\"",
                    "/new_session title:\"Climate Models\" description:\"Exploring advanced climate prediction models\""
                ],
                "notes": "A session provides a context for organizing your research. Agents, meetings, and brainstorming sessions can be associated with a specific research session."
            },
            
            "show_sessions": {
                "category": "Session",
                "description": "List active research sessions",
                "usage": "/show_sessions [limit:10]",
                "parameters": [
                    {"name": "limit", "description": "Maximum number of sessions to display", "required": False}
                ],
                "examples": [
                    "/show_sessions",
                    "/show_sessions limit:5"
                ],
                "notes": "Displays your active research sessions with their IDs, which you'll need for other commands."
            },
            
            "end_session": {
                "category": "Session",
                "description": "End an active research session",
                "usage": "/end_session session_id:\"session_id\"",
                "parameters": [
                    {"name": "session_id", "description": "ID of the session to end", "required": True}
                ],
                "examples": [
                    "/end_session session_id:\"abc123\""
                ],
                "notes": "This marks a session as completed but doesn't delete any data associated with it."
            },
            
            # Agent commands
            "create_agent": {
                "category": "Agent",
                "description": "Create a new AI research agent with specialized expertise",
                "usage": "/create_agent name:\"Agent Name\" role:\"Role\" [expertise:\"Expertise areas\"] [goal:\"Agent goal\"] [provider:\"LLM provider\"]",
                "parameters": [
                    {"name": "name", "description": "Name of the agent", "required": True},
                    {"name": "role", "description": "Role of the agent (e.g., Principal Investigator, Domain Expert, etc.)", "required": True},
                    {"name": "expertise", "description": "Areas of expertise for this agent", "required": False},
                    {"name": "goal", "description": "The agent's primary goal or focus", "required": False},
                    {"name": "provider", "description": "LLM provider to use (openai, anthropic, mistral)", "required": False}
                ],
                "examples": [
                    "/create_agent name:\"Dr. Smith\" role:\"Principal Investigator\" expertise:\"Quantum Physics\"",
                    "/create_agent name:\"BioAnalyst\" role:\"Domain Expert\" expertise:\"Genetics, CRISPR\" goal:\"Identify novel gene therapies\" provider:\"anthropic\""
                ],
                "notes": "Agents represent specialized AI personas with specific expertise that can participate in meetings and brainstorming sessions."
            },
            
            "list_agents": {
                "category": "Agent",
                "description": "List available research agents",
                "usage": "/list_agents [role:\"Optional role filter\"] [session_id:\"Optional session ID\"]",
                "parameters": [
                    {"name": "role", "description": "Filter agents by role", "required": False},
                    {"name": "session_id", "description": "Filter agents by session", "required": False}
                ],
                "examples": [
                    "/list_agents",
                    "/list_agents role:\"Domain Expert\"",
                    "/list_agents session_id:\"abc123\""
                ],
                "notes": "Shows all agents available for meetings and brainstorming sessions."
            },
            
            "edit_agent": {
                "category": "Agent",
                "description": "Edit an existing agent",
                "usage": "/edit_agent agent_id:\"agent_id\" [name:\"New name\"] [role:\"New role\"] [expertise:\"New expertise\"] [goal:\"New goal\"] [provider:\"New LLM provider\"]",
                "parameters": [
                    {"name": "agent_id", "description": "ID of the agent to edit", "required": True},
                    {"name": "name", "description": "New name for the agent", "required": False},
                    {"name": "role", "description": "New role for the agent", "required": False},
                    {"name": "expertise", "description": "New expertise areas", "required": False},
                    {"name": "goal", "description": "New agent goal", "required": False},
                    {"name": "provider", "description": "New LLM provider", "required": False}
                ],
                "examples": [
                    "/edit_agent agent_id:\"abc123\" name:\"Dr. Johnson\" expertise:\"Updated expertise\"",
                    "/edit_agent agent_id:\"abc123\" provider:\"mistral\""
                ],
                "notes": "You only need to include the parameters you want to change."
            },
            
            "delete_agent": {
                "category": "Agent",
                "description": "Delete an agent",
                "usage": "/delete_agent agent_id:\"agent_id\"",
                "parameters": [
                    {"name": "agent_id", "description": "ID of the agent to delete", "required": True}
                ],
                "examples": [
                    "/delete_agent agent_id:\"abc123\""
                ],
                "notes": "This permanently removes the agent. This action cannot be undone."
            },
            
            # Meeting commands
            "meeting": {
                "category": "Meeting",
                "description": "Start a one-on-one meeting with an agent",
                "usage": "/meeting agent_id:\"agent_id\" agenda:\"Meeting agenda\" [session_id:\"Optional session ID\"] [context:\"Additional context\"]",
                "parameters": [
                    {"name": "agent_id", "description": "ID of the agent to meet with", "required": True},
                    {"name": "agenda", "description": "The main topic or question for the meeting", "required": True},
                    {"name": "session_id", "description": "Optional session ID to associate this meeting with", "required": False},
                    {"name": "context", "description": "Additional context or background information", "required": False}
                ],
                "examples": [
                    "/meeting agent_id:\"abc123\" agenda:\"Discuss latest developments in quantum computing\"",
                    "/meeting agent_id:\"abc123\" agenda:\"RNA sequencing methods\" session_id:\"def456\" context:\"Focusing on applications in cancer research\""
                ],
                "notes": "After starting a meeting, you can chat directly with the agent in the channel."
            },
            
            "end_meeting": {
                "category": "Meeting",
                "description": "End an active meeting",
                "usage": "/end_meeting [meeting_id:\"Optional meeting ID\"]",
                "parameters": [
                    {"name": "meeting_id", "description": "ID of the specific meeting to end (if multiple are active)", "required": False}
                ],
                "examples": [
                    "/end_meeting",
                    "/end_meeting meeting_id:\"abc123\""
                ],
                "notes": "Ends the meeting and generates a summary of the discussion."
            },
            
            # Brainstorm commands
            "brainstorm": {
                "category": "Brainstorm",
                "description": "Conduct a multi-agent brainstorming session on a research topic",
                "usage": "/brainstorm agenda:\"Research topic\" [agent_count:3] [rounds:3] [include_critic:true] [agent_list:\"Agent1,Agent2\"] [agenda_questions:\"Additional questions\"] [rules:\"Session rules\"] [parallel_meetings:1]",
                "parameters": [
                    {"name": "agenda", "description": "The main research topic or question", "required": True},
                    {"name": "agent_count", "description": "Number of agents to include (default: 3)", "required": False},
                    {"name": "rounds", "description": "Number of rounds of discussion (default: 3)", "required": False},
                    {"name": "include_critic", "description": "Whether to include Critic feedback (default: true)", "required": False},
                    {"name": "agent_list", "description": "Comma-separated list of specific agent IDs to include", "required": False},
                    {"name": "agenda_questions", "description": "Additional questions or points to address", "required": False},
                    {"name": "rules", "description": "Extra constraints or instructions", "required": False},
                    {"name": "parallel_meetings", "description": "Number of parallel sessions with different agent combinations (default: 1)", "required": False}
                ],
                "examples": [
                    "/brainstorm agenda:\"Novel approaches to quantum encryption\"",
                    "/brainstorm agenda:\"Climate change mitigation strategies\" agent_count:4 rounds:5 include_critic:true agenda_questions:\"Consider economic impacts. Address implementation challenges.\"",
                    "/brainstorm agenda:\"Drug delivery mechanisms\" parallel_meetings:3"
                ],
                "notes": "Brainstorming sessions involve multiple AI agents discussing a topic, with optional critique. Running parallel sessions with different agent combinations can provide diverse perspectives."
            },
            
            "cancel_brainstorm": {
                "category": "Brainstorm",
                "description": "Cancel an active brainstorming session",
                "usage": "/cancel_brainstorm",
                "parameters": [],
                "examples": [
                    "/cancel_brainstorm"
                ],
                "notes": "This will cancel all active brainstorming sessions in the current channel."
            },
            
            "compare_brainstorms": {
                "category": "Brainstorm",
                "description": "Compare multiple brainstorming sessions",
                "usage": "/compare_brainstorms meeting_ids:\"id1,id2,id3\"",
                "parameters": [
                    {"name": "meeting_ids", "description": "Comma-separated list of meeting IDs to compare", "required": True}
                ],
                "examples": [
                    "/compare_brainstorms meeting_ids:\"abc123,def456,ghi789\""
                ],
                "notes": "This generates an analysis comparing the insights and conclusions from different brainstorming sessions."
            },
            
            # Transcript commands
            "view_transcript": {
                "category": "Transcript",
                "description": "View the transcript of a completed meeting",
                "usage": "/view_transcript meeting_id:\"meeting_id\" [format:\"full\"] [export:false]",
                "parameters": [
                    {"name": "meeting_id", "description": "ID of the meeting to view", "required": True},
                    {"name": "format", "description": "Output format: 'full' or 'summary' (default: full)", "required": False},
                    {"name": "export", "description": "Export the transcript to a file (default: false)", "required": False}
                ],
                "examples": [
                    "/view_transcript meeting_id:\"abc123\"",
                    "/view_transcript meeting_id:\"abc123\" format:\"summary\"",
                    "/view_transcript meeting_id:\"abc123\" export:true"
                ],
                "notes": "The 'full' format shows the complete conversation, while 'summary' shows only the key points."
            },
            
            "list_transcripts": {
                "category": "Transcript",
                "description": "List available transcripts from recent meetings",
                "usage": "/list_transcripts [session_id:\"Optional session ID\"] [limit:10]",
                "parameters": [
                    {"name": "session_id", "description": "Optional session ID to filter by", "required": False},
                    {"name": "limit", "description": "Maximum number of transcripts to show (default: 10)", "required": False}
                ],
                "examples": [
                    "/list_transcripts",
                    "/list_transcripts session_id:\"abc123\"",
                    "/list_transcripts limit:5"
                ],
                "notes": "Shows a list of available meeting transcripts that you can view."
            },
            
            # Help command (self-reference)
            "help": {
                "category": "General",
                "description": "Display help information about Thera and available commands",
                "usage": "/help [command:\"command_name\"] [category:\"category_name\"]",
                "parameters": [
                    {"name": "command", "description": "Optional specific command to get help for", "required": False},
                    {"name": "category", "description": "Optional category to filter help by", "required": False}
                ],
                "examples": [
                    "/help",
                    "/help command:\"brainstorm\"",
                    "/help category:\"agent\""
                ],
                "notes": "Without parameters, shows an overview of all command categories."
            }
        }
        
        # Check if the command exists
        if command_name not in commands:
            await interaction.followup.send(
                f"⚠️ Unknown command: '{command_name}'. Use /help to see all available commands.",
                ephemeral=True
            )
            return
            
        # Get the command info
        cmd_info = commands[command_name]
        
        # Create the command embed
        embed = discord.Embed(
            title=f"/{command_name}",
            description=cmd_info["description"],
            color=discord.Color.blue()
        )
        
        # Add category
        embed.add_field(
            name="Category",
            value=cmd_info["category"],
            inline=True
        )
        
        # Add usage
        embed.add_field(
            name="Usage",
            value=f"`{cmd_info['usage']}`",
            inline=False
        )
        
        # Add parameters
        if cmd_info["parameters"]:
            params_text = ""
            for param in cmd_info["parameters"]:
                required = "Required" if param["required"] else "Optional"
                params_text += f"• **{param['name']}**: {param['description']} ({required})\n"
                
            embed.add_field(
                name="Parameters",
                value=params_text,
                inline=False
            )
            
        # Add examples
        if cmd_info["examples"]:
            examples_text = ""
            for example in cmd_info["examples"]:
                examples_text += f"• `{example}`\n"
                
            embed.add_field(
                name="Examples",
                value=examples_text,
                inline=False
            )
            
        # Add notes
        if cmd_info.get("notes"):
            embed.add_field(
                name="Notes",
                value=cmd_info["notes"],
                inline=False
            )
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Add the cog to the bot"""
    await bot.add_cog(
        HelpCommand(bot),
        guilds=[discord.Object(id=guild.id) for guild in bot.guilds]
    ) 