"""
Multi-agent conversation orchestrator for the Discord bot.
Manages interactions between multiple AI agents during brainstorming sessions.
"""

import asyncio
import logging
import uuid
import random
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from llm_client import LLMClient
from models import get_system_prompt, get_system_prompt_for_role, get_default_model_for_provider
from db_client import SupabaseClient

logger = logging.getLogger('orchestrator')

class BrainstormOrchestrator:
    """Orchestrates multi-agent conversations for brainstorming sessions"""
    
    def __init__(self, db_client: SupabaseClient, llm_client: LLMClient):
        self.db_client = db_client
        self.llm_client = llm_client
        self.active_sessions = {}  # Track active sessions by meeting_id
        
    async def run_brainstorm(
        self,
        session_id: str,
        meeting_id: str,
        agents: List[Dict[str, Any]],
        agenda: str,
        rounds: int = 3,
        include_critic: bool = True,
        agenda_questions: Optional[str] = None,
        rules: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Run a multi-agent brainstorming session
        
        Args:
            session_id: The current research session ID
            meeting_id: The ID of the meeting record
            agents: List of agent records to include in the brainstorming
            agenda: The main topic or research question
            rounds: Number of rounds of discussion
            include_critic: Whether to include a critic in the discussion
            agenda_questions: Additional questions or points to address
            rules: Additional rules or constraints for the session
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of transcript entries generated during the session
        """
        # Add this session to active sessions
        self.active_sessions[meeting_id] = {
            "start_time": datetime.utcnow(),
            "session_id": session_id,
            "agenda": agenda,
            "agents": [a["id"] for a in agents]
        }
        
        # Resource management: Ensure we don't overload the LLM API
        active_session_count = len(self.active_sessions)
        if active_session_count > 1:
            # Add a small delay between parallel sessions to avoid rate limits
            delay = random.uniform(1.0, 3.0) 
            await asyncio.sleep(delay)
        
        try:
            # Prepare conversation context
            conversation = []
            transcript_data = []
            
            # Check if we have a dedicated critic agent
            critic_agent = next((a for a in agents if a["role"] == "Critic"), None) if include_critic else None
            
            # If include_critic is true but no critic agent exists, create a default one
            if include_critic and not critic_agent:
                critic_agent = {
                    "id": str(uuid.uuid4()),
                    "name": "Scientific Critic",
                    "role": "Critic",
                    "expertise": "Critical analysis and evaluation",
                    "goal": "Identify flaws, suggest improvements, and ensure scientific rigor",
                    "model": "anthropic",  # Default provider
                    "sessionId": session_id
                }
                
            # Initial prompt construction
            initial_message = {
                "role": "user",
                "content": f"This is a scientific brainstorming session on the following topic:\n\n{agenda}" + 
                          (f"\n\nAdditional questions to address: {agenda_questions}" if agenda_questions else "") +
                          (f"\n\nRules: {rules}" if rules else "")
            }
            
            conversation.append(initial_message)
            
            # Add initial message to transcript
            transcript_data.append({
                "id": str(uuid.uuid4()),
                "meetingId": meeting_id,
                "role": "user",
                "agentId": None,
                "agentName": "Moderator",
                "content": initial_message["content"],
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {},
                "createdAt": datetime.utcnow().isoformat(),
                "updatedAt": datetime.utcnow().isoformat()
            })
            
            # Save initial transcript entry
            await self.db_client.create_transcript(transcript_data[-1])
            
            # Update progress if callback provided
            if progress_callback:
                await progress_callback(0, rounds, "Starting brainstorming session...")
            
            # Run the conversation for the specified number of rounds
            for round_num in range(rounds):
                # Update progress
                if progress_callback:
                    await progress_callback(round_num, rounds, f"Round {round_num + 1}/{rounds} in progress...")
                
                # Each agent takes a turn in this round
                for idx, agent in enumerate(agents):
                    # Skip if this is the critic (critic gets special handling)
                    if agent["role"] == "Critic" and include_critic:
                        continue
                    
                    # Check if this brainstorm has been canceled
                    if meeting_id not in self.active_sessions:
                        logger.info(f"Brainstorm {meeting_id} was canceled during processing")
                        return transcript_data
                    
                    # Prepare system prompt for this agent
                    system_prompt = get_system_prompt_for_role(
                        agent.get("role", "Scientist"),
                        {
                            "name": agent["name"],
                            "expertise": agent.get("expertise", ""),
                            "goal": agent.get("goal", "")
                        }
                    )
                    
                    # Add round-specific context to the system prompt
                    brainstorm_context = f"""
This is round {round_num + 1} of {rounds} in a scientific brainstorming session.
Topic: {agenda}

Your role: You are {agent["name"]}, and your perspective is valuable because of your expertise.
{f'Additional questions to consider: {agenda_questions}' if agenda_questions else ''}
{f'Special rules: {rules}' if rules else ''}

{'' if round_num == 0 else 'Build upon the ideas shared by other participants so far.'}
{'As the first contributor in this round, you should introduce a new perspective or idea.' if idx == 0 and round_num > 0 else ''}
{'You are the last contributor in this round. Try to synthesize what has been discussed.' if idx == len(agents) - 1 and round_num == rounds - 1 else ''}

Meeting ID: {meeting_id}
"""
                    
                    # Combine the role prompt with the brainstorm context
                    full_system_prompt = f"{system_prompt}\n\n{brainstorm_context}"
                    
                    # Get agent model preference
                    agent_model = agent.get("model", "anthropic")
                    agent_specific_model = get_default_model_for_provider(agent_model)
                    
                    try:
                        # Generate response from this agent
                        agent_response = await self.llm_client.chat_with_history(
                            provider=agent_model,
                            conversation=conversation,
                            system_prompt=full_system_prompt,
                            model=agent_specific_model
                        )
                        
                        # Format the agent's response to clearly indicate who is speaking
                        formatted_response = f"[{agent['name']} - {agent.get('role', 'Scientist')}]: {agent_response['text']}"
                        
                        # Append agent's response to conversation
                        agent_message = {
                            "role": "assistant",
                            "content": formatted_response
                        }
                        conversation.append(agent_message)
                        
                        # Add to transcript
                        transcript_data.append({
                            "id": str(uuid.uuid4()),
                            "meetingId": meeting_id,
                            "role": "assistant",
                            "agentId": agent["id"],
                            "agentName": agent["name"],
                            "content": agent_response["text"],
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": {
                                "tokens": agent_response.get("usage", {}),
                                "round": round_num + 1,
                                "agent_role": agent.get("role", "Scientist")
                            },
                            "createdAt": datetime.utcnow().isoformat(),
                            "updatedAt": datetime.utcnow().isoformat()
                        })
                        
                        # Save transcript entry
                        await self.db_client.create_transcript(transcript_data[-1])
                        
                        # If a critic is included and this is not the last round, add critic feedback
                        if include_critic and critic_agent:
                            # Prepare critic system prompt
                            critic_system_prompt = get_system_prompt_for_role(
                                "Critic",
                                {
                                    "name": critic_agent["name"],
                                    "expertise": critic_agent.get("expertise", "Critical analysis"),
                                    "goal": critic_agent.get("goal", "Identify flaws and suggest improvements")
                                }
                            )
                            
                            # Add critic-specific context
                            critic_context = f"""
You are reviewing the most recent contribution in a scientific brainstorming session.
Topic: {agenda}

Focus on the last response from {agent["name"]} (a {agent.get("role", "Scientist")}).
Provide brief, constructive criticism that will improve the scientific quality of the discussion.
Be concise and focus on 1-2 key points that could be improved or clarified.

Meeting ID: {meeting_id}
"""
                            
                            # Combine the prompts
                            full_critic_prompt = f"{critic_system_prompt}\n\n{critic_context}"
                            
                            # Create a copy of the conversation for the critic
                            critic_convo = conversation.copy()
                            
                            # Generate critic response
                            critic_model = critic_agent.get("model", "anthropic")
                            critic_specific_model = get_default_model_for_provider(critic_model)
                            
                            critic_response = await self.llm_client.chat_with_history(
                                provider=critic_model,
                                conversation=critic_convo,
                                system_prompt=full_critic_prompt,
                                model=critic_specific_model
                            )
                            
                            # Format the critic's response
                            formatted_critic = f"[{critic_agent['name']} - Critic]: {critic_response['text']}"
                            
                            # Append critic's feedback to conversation
                            critic_message = {
                                "role": "assistant",
                                "content": formatted_critic
                            }
                            conversation.append(critic_message)
                            
                            # Add to transcript
                            transcript_data.append({
                                "id": str(uuid.uuid4()),
                                "meetingId": meeting_id,
                                "role": "critic",
                                "agentId": critic_agent["id"],
                                "agentName": critic_agent["name"],
                                "content": critic_response["text"],
                                "timestamp": datetime.utcnow().isoformat(),
                                "metadata": {
                                    "tokens": critic_response.get("usage", {}),
                                    "round": round_num + 1,
                                    "target_agent": agent["name"]
                                },
                                "createdAt": datetime.utcnow().isoformat(),
                                "updatedAt": datetime.utcnow().isoformat()
                            })
                            
                            # Save transcript entry
                            await self.db_client.create_transcript(transcript_data[-1])
                    
                    except Exception as e:
                        logger.error(f"Error during agent {agent['name']} response in meeting {meeting_id}: {str(e)}")
                        # Add error information to transcript
                        error_transcript = {
                            "id": str(uuid.uuid4()),
                            "meetingId": meeting_id,
                            "role": "system",
                            "agentId": None,
                            "agentName": "System",
                            "content": f"Error generating response from {agent['name']}: {str(e)}",
                            "timestamp": datetime.utcnow().isoformat(),
                            "metadata": {"error": str(e)},
                            "createdAt": datetime.utcnow().isoformat(),
                            "updatedAt": datetime.utcnow().isoformat()
                        }
                        transcript_data.append(error_transcript)
                        await self.db_client.create_transcript(error_transcript)
                
                # If not the last round, add a transition message
                if round_num < rounds - 1:
                    transition_message = {
                        "role": "user",
                        "content": f"Let's continue to round {round_num + 2} of our brainstorming session on {agenda}. Please build upon the ideas shared so far."
                    }
                    conversation.append(transition_message)
                    
                    # Add to transcript
                    transcript_data.append({
                        "id": str(uuid.uuid4()),
                        "meetingId": meeting_id,
                        "role": "user",
                        "agentId": None,
                        "agentName": "Moderator",
                        "content": transition_message["content"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {"round_transition": round_num + 1},
                        "createdAt": datetime.utcnow().isoformat(),
                        "updatedAt": datetime.utcnow().isoformat()
                    })
                    
                    # Save transcript entry
                    await self.db_client.create_transcript(transcript_data[-1])
            
            # Update progress
            if progress_callback:
                await progress_callback(rounds, rounds, "Generating summary...")
            
            # Generate a concise summary of the brainstorming session
            system_prompt = """You are a skilled research assistant. Your task is to create a concise yet comprehensive summary
of the key ideas and insights from the brainstorming session. Focus on:
1. Main themes and concepts discussed
2. Novel ideas or approaches proposed
3. Points of consensus among participants
4. Areas of disagreement or uncertainty
5. Potential next steps or research directions

Keep your summary clear and well-structured."""
            
            summary_conversation = [
                {"role": "user", "content": f"Here is a brainstorming session on '{agenda}'. Please provide a comprehensive summary:\n\n" + 
                 "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation])}
            ]
            
            try:
                summary_response = await self.llm_client.chat_with_history(
                    provider="anthropic",  # Defaulting to Anthropic for summaries
                    conversation=summary_conversation,
                    system_prompt=system_prompt
                )
                
                # Add summary to transcript
                summary_transcript = {
                    "id": str(uuid.uuid4()),
                    "meetingId": meeting_id,
                    "role": "system",
                    "agentId": None,
                    "agentName": "System",
                    "content": summary_response["text"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"type": "summary"},
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
                transcript_data.append(summary_transcript)
                await self.db_client.create_transcript(summary_transcript)
                
                # Update meeting record with summary
                await self.db_client.update_meeting(meeting_id, {
                    "summary": summary_response["text"],
                    "endedAt": datetime.utcnow().isoformat(),
                    "status": "completed",
                    "updatedAt": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error generating session summary for meeting {meeting_id}: {str(e)}")
                # Still mark the meeting as completed
                await self.db_client.update_meeting(meeting_id, {
                    "endedAt": datetime.utcnow().isoformat(),
                    "status": "completed",
                    "updatedAt": datetime.utcnow().isoformat()
                })
            
            # Update final progress
            if progress_callback:
                await progress_callback(rounds, rounds, "Brainstorming session completed")
            
            # Remove from active sessions
            if meeting_id in self.active_sessions:
                del self.active_sessions[meeting_id]
                
            return transcript_data 
        
        except Exception as e:
            logger.error(f"Unexpected error in meeting {meeting_id}: {str(e)}")
            
            # Clean up the active sessions tracker
            if meeting_id in self.active_sessions:
                del self.active_sessions[meeting_id]
                
            # Ensure the meeting is marked as error
            try:
                await self.db_client.update_meeting(meeting_id, {
                    "endedAt": datetime.utcnow().isoformat(),
                    "status": "error",
                    "metadata": {"error": str(e)},
                    "updatedAt": datetime.utcnow().isoformat()
                })
            except Exception as update_error:
                logger.error(f"Error updating meeting status: {str(update_error)}")
                
            # Re-raise the exception
            raise
            
    async def cancel_brainstorm(self, meeting_id: str) -> bool:
        """
        Cancel an active brainstorming session
        
        Args:
            meeting_id: The ID of the meeting to cancel
            
        Returns:
            True if the meeting was successfully canceled, False otherwise
        """
        if meeting_id not in self.active_sessions:
            return False
            
        # Remove from active sessions
        del self.active_sessions[meeting_id]
        
        # Update meeting status
        try:
            await self.db_client.update_meeting(meeting_id, {
                "endedAt": datetime.utcnow().isoformat(),
                "status": "canceled",
                "updatedAt": datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            logger.error(f"Error canceling meeting {meeting_id}: {str(e)}")
            return False 