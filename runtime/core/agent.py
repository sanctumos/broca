"""Agent API client and operations."""
from typing import Optional, Dict, Any, List
import logging
from letta_client import MessageCreate
from .letta_client import get_letta_client
from common.config import get_env_var
from common.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class AgentClient:
    """Client for interacting with the agent API."""
    
    def __init__(self):
        """Initialize the agent client with configuration."""
        self.debug_mode = get_env_var("DEBUG_MODE", default="false", cast_type=lambda x: x.lower() == "true")
        self.agent_id = get_env_var("AGENT_ID", required=not self.debug_mode)
        
        logger.debug(f"Initializing AgentClient with ID: {self.agent_id}")
        logger.debug(f"Debug mode: {self.debug_mode}")
        
        if not self.debug_mode and not self.agent_id:
            raise ValueError(
                "Missing required environment variable. Please ensure AGENT_ID "
                "is set in your .env file, or set DEBUG_MODE=true to run in "
                "debug mode without an agent API."
            )
    
    async def initialize(self) -> bool:
        """Initialize the agent connection."""
        if self.debug_mode:
            logger.info("🔧 Running in debug mode - agent API disabled")
            return True
            
        try:
            # Get the singleton Letta client
            client = get_letta_client()
            logger.debug("Retrieved Letta client instance")
            
            # Verify agent exists
            logger.debug(f"Attempting to retrieve agent {self.agent_id}")
            try:
                agent = client.agents.retrieve(self.agent_id)
                logger.info(f"✅ Connected to agent {agent.id}: {agent.name}")
                return True
            except Exception as e:
                logger.error(f"❌ Agent {self.agent_id} not found: {str(e)}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Letta client: {str(e)}")
            return False
    
    async def process_message(self, message: str) -> Optional[str]:
        """Process a message through the agent API."""
        if self.debug_mode:
            logger.debug(f"Debug mode: returning message without processing: {message}")
            return message
            
        try:
            client = get_letta_client()
            
            logger.debug(f"Sending message to agent {self.agent_id}: {message}")
            response = client.agents.messages.create(
                agent_id=self.agent_id,
                messages=[MessageCreate(role="user", content=message)]
            )
            
            logger.debug(f"Received response: {response}")
            
            if not hasattr(response, 'messages'):
                logger.error("Response does not have 'messages' attribute")
                return None
                
            if not response.messages:
                logger.warning("No messages in response")
                return None
                
            response_content = None
            for msg in response.messages:
                logger.debug(f"Processing message: id={msg.id}, type={msg.message_type}")
                
                if msg.message_type == 'reasoning_message':
                    logger.debug(f"Found reasoning: {msg.reasoning}")
                    continue
                    
                if hasattr(msg, 'content'):
                    response_content = msg.content
                    break
            
            if response_content is None:
                logger.error("No response content found in any message")
                for msg in response.messages:
                    if msg.message_type == 'reasoning_message' and hasattr(msg, 'reasoning'):
                        response_content = msg.reasoning
                        break
            
            return response_content
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None
    
    async def cleanup(self) -> None:
        """Clean up any resources used by the agent client."""
        pass 