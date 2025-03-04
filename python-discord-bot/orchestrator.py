import logging
import asyncio
from typing import List, Dict, Optional, Any, Set
from models import LLMProvider, LLMMessage

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates agent interactions in meetings."""
    
    def __init__(self, llm_client):
        """Initialize the orchestrator with an LLM client."""
        self.llm_client = llm_client
        self.active_meetings = {}
        self.parallel_groups = {}
        logger.info("Initialized AgentOrchestrator")
    
    async def initialize_meeting(self, meeting_id, session_id, agents, agenda, round_count, parallel_index=0):
        """Initialize a new meeting."""
        logger.info("Initializing meeting " + str(meeting_id))
        self.active_meetings[meeting_id] = {
            "id": meeting_id,
            "session_id": session_id,
            "agents": agents,
            "agenda": agenda,
            "round_count": round_count,
            "current_round": 0,
            "is_completed": False,
            "thread": None,
            "parallel_index": parallel_index,
            "messages": [],
            "is_active": True,
            "summary": None
        }
        
        # Track parallel meetings
        if session_id not in self.parallel_groups:
            self.parallel_groups[session_id] = set()
        self.parallel_groups[session_id].add(meeting_id)
        
        logger.info("Initialized meeting " + str(meeting_id) + " (parallel index " + str(parallel_index) + ") for session " + str(session_id))
        return True
    
    async def start_conversation(self, meeting_id, interaction, live_mode=True):
        """Start a conversation for a meeting.
        
        Args:
            meeting_id: ID of the meeting
            interaction: Discord interaction object
            live_mode: Whether to output agent responses in real-time (default: True)
        """
        logger.info("Starting conversation for meeting " + str(meeting_id) + " (live_mode: " + str(live_mode) + ")")
        
        # Store live_mode setting in meeting data for reference by the server-side code
        meeting_data = self.active_meetings.get(meeting_id)
        if meeting_data:
            meeting_data["live_mode"] = live_mode
            
        return True
    
    async def end_conversation(self, meeting_id):
        """End a conversation for a meeting.
        
        Args:
            meeting_id: ID of the meeting
        """
        logger.info("Ending conversation for meeting " + str(meeting_id))
        
        meeting_data = self.active_meetings.get(meeting_id)
        if meeting_data:
            meeting_data["is_completed"] = True
            meeting_data["is_active"] = False
            
        return True
    
    async def generate_combined_summary(self, meetings):
        """Generate a combined summary of parallel meetings."""
        logger.info("Generating combined summary for " + str(len(meetings)) + " meetings")
        
        # Extract summaries from each meeting
        parallel_summaries = []
        for meeting in meetings:
            if meeting.get("summary"):
                parallel_summaries.append(meeting.get("summary"))
        
        # If only one meeting or no summaries, return the single summary
        if len(parallel_summaries) <= 1:
            return parallel_summaries[0] if parallel_summaries else "No summary available."
        
        # Create a prompt for combining the summaries
        messages = [
            LLMMessage(
                role="system",
                content="You are an expert research synthesizer. Your task is to combine multiple parallel brainstorming sessions into a cohesive summary."
            ),
            LLMMessage(
                role="user",
                content="Topic: " + meetings[0]['agenda'] + "\n\nParticipants: " + ", ".join(agent['name'] for agent in meetings[0]['agents']) + "\n\nIndividual Run Summaries:\n" + "\n\n".join(parallel_summaries) + "\n\nProvide a synthesis that includes:\n1. Common themes and consensus across runs\n2. Unique insights and novel approaches from each run\n3. Contrasting perspectives and alternative solutions\n4. Integrated conclusions and recommendations\n5. Key areas for further investigation"
            )
        ]
        
        try:
            response = await self.llm_client.generate_response(
                provider=LLMProvider.OPENAI,
                messages=messages,
                temperature=0.7
            )
            
            return response.content
            
        except Exception as e:
            logger.error("Error generating combined summary: " + str(e))
            return "Error generating combined summary." 