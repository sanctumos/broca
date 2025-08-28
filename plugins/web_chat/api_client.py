"""
API Client for Web Chat Bridge

This module handles communication with the PHP-based web chat bridge API,
including polling for new messages and posting responses.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from plugins.web_chat.settings import WebChatSettings


class WebChatAPIClient:
    """Client for communicating with the Web Chat Bridge API."""
    
    def __init__(self, settings: WebChatSettings):
        self.settings = settings
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            'Authorization': f'Bearer {self.settings.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Broca2-WebChat-Plugin/1.0'
        }
        self.logger.debug(f"🔍 API Key: {self.settings.api_key[:10]}..." if self.settings.api_key else "🔍 API Key: None/Empty")
        self.logger.debug(f"🔍 Request Headers: {headers}")
        return headers
    
    async def get_messages(self, limit: int = 50, offset: int = 0, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Poll for new messages from the web chat API.
        
        Args:
            limit: Maximum number of messages to retrieve
            offset: Number of messages to skip
            since: ISO timestamp to get messages since specific time
            
        Returns:
            List of message dictionaries
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {
            'action': 'inbox',
            'limit': min(limit, 100),  # API max is 100
            'offset': offset
        }
        
        if since:
            params['since'] = since
        
        try:
            url = f"{self.settings.api_url}/api/v1/"
            self.logger.debug(f"🔍 Making request to: {url}")
            self.logger.debug(f"🔍 Request params: {params}")
            
            async with self.session.get(
                url,
                headers=self._get_headers(),
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        messages = data.get('data', {}).get('messages', [])
                        self.logger.info(f"Retrieved {len(messages)} messages from web chat API")
                        return messages
                    else:
                        self.logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
                        return []
                else:
                    self.logger.error(f"API request failed with status {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error polling for messages: {e}")
            return []
    
    async def post_response(self, session_id: str, response: str) -> bool:
        """
        Post a response back to the web chat API.
        
        Args:
            session_id: The session ID to post the response to
            response: The response message to post
            
        Returns:
            True if successful, False otherwise
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        data = {
            'session_id': session_id,
            'response': response
        }
        
        try:
            async with self.session.post(
                f"{self.settings.api_url}/api/v1/",
                headers=self._get_headers(),
                params={'action': 'outbox'},
                json=data
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get('success'):
                        self.logger.info(f"Successfully posted response to session {session_id}")
                        return True
                    else:
                        self.logger.error(f"Failed to post response: {response_data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.logger.error(f"Failed to post response, status {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Error posting response: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test the connection to the web chat API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            messages = await self.get_messages(limit=1)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False 