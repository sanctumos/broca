"""
Letta API client implementation using the official SDK.

Letta 1.x compliance (SDK 1.7.x):
- No top-level identities: use create_identity() (POST /v1/identities/) instead.
- Sync SDK (Letta) is used; all sync calls from async code are run via
  asyncio.to_thread() in runtime.core.agent and runtime.core.queue.
- Blocks: client.blocks for global blocks; client.agents.blocks for
  agent core-memory attach/detach. Both exist in 1.x.
"""

import logging
from typing import Any

import httpx
from letta_client import Letta

from common.config import get_env_var

# Set up logging
logger = logging.getLogger(__name__)


class _IdentityCreateResponse:
    """Minimal response type for identity create (SDK 1.7.x has no top-level identities)."""

    def __init__(self, id: str, **kwargs: Any) -> None:
        self.id = id


class LettaClient:
    """Client for interacting with the Letta API."""

    def __init__(self):
        """Initialize the Letta client with configuration from settings."""
        self.api_endpoint = get_env_var("AGENT_ENDPOINT")
        self.api_key = get_env_var("AGENT_API_KEY")

        logger.debug(f"Initializing Letta client with endpoint: {self.api_endpoint}")
        # API key is not logged for security reasons

        # Initialize the official Letta client (SDK may use token= or api_key=).
        try:
            self._client = Letta(
                base_url=self.api_endpoint, token=self.api_key, timeout=60.0
            )
        except TypeError:
            self._client = Letta(
                base_url=self.api_endpoint, api_key=self.api_key, max_retries=0
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
    def conversations(self):
        """Get the conversations API client."""
        return self._client.conversations

    @property
    def runs(self):
        """Get the runs API client."""
        return self._client.runs

    @property
    def messages(self):
        """Get the top-level messages API (list/retrieve by message_id)."""
        return self._client.messages

    async def create_identity(
        self,
        *,
        identifier_key: str,
        name: str,
        identity_type: str = "user",
    ) -> _IdentityCreateResponse:
        """
        Create a Letta identity via POST /v1/identities/.
        The official SDK 1.7.x does not expose top-level identities, so we call the API directly.
        """
        url = f"{self.api_endpoint.rstrip('/')}/v1/identities/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        body = {
            "identifier_key": identifier_key,
            "name": name,
            "identity_type": identity_type,
        }
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
        return _IdentityCreateResponse(id=data["id"])

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
