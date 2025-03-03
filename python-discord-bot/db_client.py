import os
import logging
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union

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
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (will be appended to base URL)
            data: Optional JSON data to send
            params: Optional query parameters
            
        Returns:
            API response as a dictionary
        
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            try:
                logger.debug(f"Making {method} request to {url}")
                
                if method == "GET":
                    async with session.get(url, params=params, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"API error ({response.status}): {error_text}")
                            return {"isSuccess": False, "message": f"API error: {response.status}", "data": None}
                        
                        result = await response.json()
                        return result
                
                elif method == "POST":
                    async with session.post(url, json=data, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"API error ({response.status}): {error_text}")
                            return {"isSuccess": False, "message": f"API error: {response.status}", "data": None}
                        
                        result = await response.json()
                        return result
                
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
        return await self._make_request("GET", f"/api/discord/sessions/active", params={"userId": user_id})
    
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
            "userId": user_id,
            "title": title,
            "isPublic": is_public
        }
        
        if description:
            data["description"] = description
            
        return await self._make_request("POST", "/api/discord/sessions", data)
    
    # Meeting-related methods
    async def create_meeting(
        self, 
        session_id: str, 
        title: str, 
        agenda: Optional[str] = None,
        task_description: Optional[str] = None,
        max_rounds: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new meeting in a session.
        
        Args:
            session_id: ID of the session
            title: Title of the meeting
            agenda: Optional agenda for the meeting
            task_description: Optional task description for the meeting
            max_rounds: Optional maximum number of rounds for the meeting
            
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
            
        return await self._make_request("POST", "/api/discord/meetings", data)
    
    async def end_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """End a meeting.
        
        Args:
            meeting_id: ID of the meeting
            
        Returns:
            Meeting data or error information
        """
        return await self._make_request("PUT", f"/api/discord/meetings/{meeting_id}/end")
    
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
            
        return await self._make_request("POST", "/api/discord/transcripts", data)

# Create a singleton instance
db_client = DatabaseClient() 