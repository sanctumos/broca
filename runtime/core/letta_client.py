"""
Letta API client implementation using the official SDK.
"""

import logging

from letta_client import Letta

from common.config import get_env_var

# Set up logging
logger = logging.getLogger(__name__)


class LettaClient:
    """Client for interacting with the Letta API."""

    def __init__(self):
        """Initialize the Letta client with configuration from settings."""
        self.api_endpoint = get_env_var("AGENT_ENDPOINT")
        self.api_key = get_env_var("AGENT_API_KEY")

        logger.debug(f"Initializing Letta client with endpoint: {self.api_endpoint}")
        # API key is not logged for security reasons

        # Initialize the official Letta client
        self._client = Letta(base_url=self.api_endpoint, token=self.api_key)

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
_letta_client: LettaClient | None = None


def get_letta_client() -> LettaClient:
    """Get the Letta client singleton instance."""
    global _letta_client
    if _letta_client is None:
        _letta_client = LettaClient()
    return _letta_client
