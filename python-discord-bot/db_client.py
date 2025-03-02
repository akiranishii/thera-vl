"""
Database client for connecting to Supabase.
Handles CRUD operations for the Discord bot.
"""

import os
import json
import logging
import httpx
from typing import Dict, List, Any, Optional, Union
from config import Config

logger = logging.getLogger('db_client')

class SupabaseClient:
    """Client for interacting with Supabase database"""
    
    def __init__(self):
        self.base_url = Config.DB_HOST
        self.key = Config.DB_PASSWORD
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        if not self.base_url or not self.key:
            logger.error("Missing Supabase credentials. Please check your environment variables.")
            raise ValueError("Missing Supabase credentials")
        
        # Strip trailing slash if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to Supabase REST API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{path}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=10.0
                )
                
                response.raise_for_status()
                
                if response.status_code == 204:  # No content
                    return {}
                    
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    # Sessions table operations
    
    async def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session"""
        return await self._request("POST", "/rest/v1/sessions", data=data)
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a session by ID"""
        params = {"id": f"eq.{session_id}"}
        result = await self._request("GET", "/rest/v1/sessions", params=params)
        return result[0] if result else None
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a session by ID"""
        params = {"id": f"eq.{session_id}"}
        return await self._request("PATCH", "/rest/v1/sessions", params=params, data=data)
    
    # Agents table operations
    
    async def create_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        return await self._request("POST", "/rest/v1/agents", data=data)
    
    async def get_agents(self, filters: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Get agents with optional filtering"""
        params = {}
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
                
        return await self._request("GET", "/rest/v1/agents", params=params)
    
    async def update_agent(self, agent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an agent by ID"""
        params = {"id": f"eq.{agent_id}"}
        return await self._request("PATCH", "/rest/v1/agents", params=params, data=data)
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent by ID"""
        params = {"id": f"eq.{agent_id}"}
        return await self._request("DELETE", "/rest/v1/agents", params=params)
    
    # Meetings table operations
    
    async def create_meeting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new meeting"""
        return await self._request("POST", "/rest/v1/meetings", data=data)
    
    async def get_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Get a meeting by ID"""
        params = {"id": f"eq.{meeting_id}"}
        result = await self._request("GET", "/rest/v1/meetings", params=params)
        return result[0] if result else None
    
    async def get_meetings_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all meetings for a session"""
        params = {"sessionId": f"eq.{session_id}"}
        return await self._request("GET", "/rest/v1/meetings", params=params)
    
    async def update_meeting(self, meeting_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a meeting by ID"""
        params = {"id": f"eq.{meeting_id}"}
        return await self._request("PATCH", "/rest/v1/meetings", params=params, data=data)
    
    # Transcripts table operations
    
    async def create_transcript(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transcript entry"""
        return await self._request("POST", "/rest/v1/transcripts", data=data)
    
    async def get_transcripts_by_meeting(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get all transcripts for a meeting"""
        params = {"meetingId": f"eq.{meeting_id}"}
        return await self._request("GET", "/rest/v1/transcripts", params=params)
    
    # Utility methods
    
    async def check_connection(self) -> bool:
        """Test the database connection"""
        try:
            # Try to get a single row from any table to test connection
            await self._request("HEAD", "/rest/v1/sessions")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False 