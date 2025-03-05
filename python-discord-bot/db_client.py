import os
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
import asyncio

from config import API_BASE_URL

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Client for interacting with the application's database via API calls."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the database client with the base API URL.
        
        Args:
            base_url: Base URL for the API endpoints
        """
        self.base_url = base_url
        logger.info(f"DatabaseClient initialized with base URL: {base_url}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the API is reachable.
        
        Returns:
            Status information
        """
        try:
            # Just try to reach the base API to check connectivity
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        return {"isSuccess": True, "message": "API is reachable", "data": None}
                    else:
                        return {"isSuccess": False, "message": f"API returned status {response.status}", "data": None}
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error during health check: {str(e)}")
            return {"isSuccess": False, "message": f"Cannot connect to API: {str(e)}", "data": None}
        except asyncio.TimeoutError:
            logger.error("Timeout during health check")
            return {"isSuccess": False, "message": "API connection timed out", "data": None}
        except Exception as e:
            logger.error(f"Error during health check: {str(e)}")
            return {"isSuccess": False, "message": f"API check failed: {str(e)}", "data": None}
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data or error information
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
            
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        logger.debug(f"Making {method} request to {url}")
        if params:
            logger.debug(f"Request params: {params}")
        if data:
            logger.debug(f"Request data: {data}")
        
        try:
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    try:
                        async with session.get(url, params=params, headers=headers) as response:
                            if response.status >= 400:
                                error_text = await response.text()
                                logger.error(f"API error ({response.status}): {error_text}")
                                return {"isSuccess": False, "message": f"API error ({response.status}): {error_text}", "data": None}
                            
                            result = await response.json()
                            logger.debug(f"Response from {url}: {result}")
                            return result
                    except aiohttp.ClientConnectorError as e:
                        logger.error(f"HTTP error: {str(e)}")
                        return {"isSuccess": False, "message": f"Cannot connect to API: {str(e)}", "data": None}
                
                elif method == "POST":
                    try:
                        async with session.post(url, json=data, headers=headers) as response:
                            if response.status >= 400:
                                error_text = await response.text()
                                logger.error(f"API error ({response.status}): {error_text}")
                                return {"isSuccess": False, "message": f"API error ({response.status}): {error_text}", "data": None}
                            
                            result = await response.json()
                            logger.debug(f"Response from {url}: {result}")
                            return result
                    except aiohttp.ClientConnectorError as e:
                        logger.error(f"HTTP error: {str(e)}")
                        return {"isSuccess": False, "message": f"Cannot connect to API: {str(e)}", "data": None}
                
                elif method == "PUT":
                    async with session.put(url, json=data, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"API error ({response.status}): {error_text}")
                            return {"isSuccess": False, "message": f"API error: {response.status}", "data": None}
                        
                        result = await response.json()
                        return result
                
                elif method == "DELETE":
                    async with session.delete(url, json=data, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"API error ({response.status}): {error_text}")
                            return {"isSuccess": False, "message": f"API error: {response.status}", "data": None}
                        
                        result = await response.json()
                        return result
                
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error: {str(e)}")
            return {"isSuccess": False, "message": f"HTTP error: {str(e)}", "data": None}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"isSuccess": False, "message": f"Unexpected error: {str(e)}", "data": None}
    
    # Session-related methods
    async def get_active_session(self, user_id: str) -> Dict[str, Any]:
        """Get the active session for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Session data or error information
        """
        return await self._make_request("GET", f"/discord/sessions/active", params={"userId": user_id})
    
    async def create_session(
        self, 
        user_id: str, 
        title: str, 
        description: Optional[str] = None,
        is_public: bool = False
    ) -> Dict[str, Any]:
        """Create a new session.
        
        Args:
            user_id: ID of the user
            title: Title of the session
            description: Optional description of the session
            is_public: Whether the session is public
            
        Returns:
            Session data or error information
        """
        data = {
            "userId": user_id,  # The API expects "userId"
            "title": title,
            "isPublic": is_public
        }
        
        if description:
            data["description"] = description
            
        # Log the data being sent
        logger.debug(f"Sending session creation data: {data}")
            
        return await self._make_request("POST", "/discord/sessions", data)
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session data or error information
        """
        return await self._make_request("PUT", f"/discord/sessions/{session_id}/end")
    
    async def get_session_agents(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get agents for a session.
        
        Args:
            session_id: ID of the session
            user_id: ID of the user
            
        Returns:
            Agents data or error information
        """
        return await self._make_request(
            "GET", 
            f"/discord/sessions/{session_id}/agents", 
            params={"userId": user_id}
        )
    
    # Agent-related methods
    async def create_agent(
        self,
        session_id: str,
        name: str,
        role: str,
        goal: Optional[str] = None,
        expertise: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new agent.
        
        Args:
            session_id: ID of the session
            name: Name of the agent
            role: Role of the agent
            goal: Optional goal or description of the agent
            expertise: Optional area of expertise
            model: Optional model to use for the agent
            
        Returns:
            Agent data or error information
        """
        data = {
            "userId": session_id,  # Using sessionId as userId for now
            "sessionId": session_id,
            "name": name,
            "role": role
        }
        
        if goal:
            data["description"] = goal
        if expertise:
            data["expertise"] = expertise
        if model:
            data["model"] = model
            
        return await self._make_request("POST", "/discord/agents", data)
    
    # Meeting-related methods
    async def create_meeting(
        self, 
        session_id: str, 
        title: str, 
        agenda: Optional[str] = None,
        task_description: Optional[str] = None,
        max_rounds: Optional[int] = None,
        parallel_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new meeting in a session.
        
        Args:
            session_id: ID of the session
            title: Title of the meeting
            agenda: Optional agenda for the meeting
            task_description: Optional task description for the meeting
            max_rounds: Optional maximum number of rounds for the meeting
            parallel_index: Optional index for parallel meetings
            
        Returns:
            Meeting data or error information
        """
        data = {
            "sessionId": session_id,
            "title": title
        }
        
        if agenda:
            data["agenda"] = agenda
        if task_description:
            data["taskDescription"] = task_description
        if max_rounds:
            data["maxRounds"] = max_rounds
        if parallel_index is not None:  # Use is not None to allow 0 as a valid value
            data["parallelIndex"] = parallel_index
            
        return await self._make_request("POST", "/discord/meetings", data)
    
    async def end_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """End a meeting.
        
        Args:
            meeting_id: ID of the meeting
            
        Returns:
            Meeting data or error information
        """
        return await self._make_request("PUT", f"/discord/meetings/{meeting_id}/end")
    
    # Transcript-related methods
    async def add_message(
        self, 
        meeting_id: str, 
        content: str, 
        role: str, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a message to a meeting transcript.
        
        Args:
            meeting_id: ID of the meeting
            content: Content of the message
            role: Role of the message sender (user, assistant, system)
            user_id: Optional ID of the user (for user messages)
            
        Returns:
            Message data or error information
        """
        data = {
            "meetingId": meeting_id,
            "content": content,
            "role": role
        }
        
        if user_id:
            data["userId"] = user_id
            
        return await self._make_request("POST", "/discord/transcripts", data)

# Create a singleton instance
db_client = DatabaseClient() 