"""
Letta API client implementation using the official SDK.
"""

import os
import logging
from typing import Optional
from letta_client import Letta
from .config import settings

# Set up logging
logger = logging.getLogger(__name__)

class LettaClient:
    """Client for interacting with the Letta API."""
    
    def __init__(self):
        """Initialize the Letta client with configuration from settings."""
        self.api_endpoint = settings.agent_endpoint
        self.api_key = settings.agent_api_key
        
        logger.debug(f"Initializing Letta client with endpoint: {self.api_endpoint}")
        logger.debug(f"Using API key: {self.api_key[:4]}...")
        
        # Initialize the official Letta client
        self._client = Letta(
            base_url=self.api_endpoint,
            token=self.api_key
        )
    
    @property
    def client(self):
        """Get the underlying Letta client instance."""
        return self._client
    
    @property
    def agents(self):
        """Get the agents API client."""
        return self._client.agents
    
    @property
    def blocks(self):
        """Get the blocks API client."""
        return self._client.blocks
    
    @property
    def identities(self):
        """Get the identities API client."""
        return self._client.identities
    
    def close(self):
        """Close the client."""
        # The official client doesn't need explicit closing
        pass

# Create a singleton instance
_letta_client: Optional[LettaClient] = None

def get_letta_client() -> LettaClient:
    """Get the Letta client singleton instance."""
    global _letta_client
    if _letta_client is None:
        _letta_client = LettaClient()
    return _letta_client 