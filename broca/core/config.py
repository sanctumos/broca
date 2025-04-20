"""
Configuration management for the Broca application.
This module centralizes all environment variable handling and provides type-safe access to configuration values.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings with validation and type hints."""
    
    # Letta API Configuration
    letta_api_endpoint: str = Field(..., env="LETTA_API_ENDPOINT")
    letta_api_key: str = Field(..., env="LETTA_API_KEY")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Agent Configuration
    agent_id: str = Field(..., env="AGENT_ID")
    debug_mode: bool = Field(False, env="DEBUG_MODE")
    agent_api_key: str = Field(..., env="AGENT_API_KEY")
    agent_endpoint: str = Field(..., env="AGENT_ENDPOINT")
    
    # Telegram Configuration
    telegram_api_id: str = Field(..., env="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(..., env="TELEGRAM_API_HASH")
    telegram_phone: str = Field(..., env="TELEGRAM_PHONE")
    telegram_group_chat_id: str = Field(..., env="TELEGRAM_GROUP_CHAT_ID")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # Allow extra fields in the environment
    )
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate that environment is one of the allowed values."""
        allowed = {"development", "production", "test"}
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()
    
    @validator("debug_mode", pre=True)
    def validate_debug_mode(cls, v):
        """Convert debug mode string to boolean."""
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)

# Create a singleton instance of settings
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get the application settings singleton instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Export commonly used settings for convenience
settings = get_settings() 