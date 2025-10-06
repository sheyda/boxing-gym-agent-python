"""Configuration management for the Boxing Gym Agent."""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from Secret Manager with environment variable fallback."""
    
    # Google API Configuration
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:8080/oauth2callback",
        env="GOOGLE_REDIRECT_URI"
    )
    
    # Gmail Configuration
    gmail_user_email: str = Field(..., env="GMAIL_USER_EMAIL")
    gmail_query: str = Field(
        default="from:boxing_gym@gmail.com subject:class registration",
        env="GMAIL_QUERY"
    )
    
    # Boxing Gym Configuration
    boxing_gym_email: str = Field(..., env="BOXING_GYM_EMAIL")
    boxing_gym_name: str = Field(default="Boxing Gym", env="BOXING_GYM_NAME")
    
    # Calendar Configuration
    calendar_id: str = Field(default="primary", env="CALENDAR_ID")
    event_duration_minutes: int = Field(default=60, env="EVENT_DURATION_MINUTES")
    timezone: str = Field(default="America/New_York", env="TIMEZONE")
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    llm_model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    
    # Agent Configuration
    check_interval_minutes: int = Field(default=5, env="CHECK_INTERVAL_MINUTES")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_emails_per_check: int = Field(default=10, env="MAX_EMAILS_PER_CHECK")
    
    # Processing Configuration
    confidence_threshold: float = Field(default=0.7, env="CONFIDENCE_THRESHOLD")
    enable_auto_registration: bool = Field(default=False, env="ENABLE_AUTO_REGISTRATION")
    enable_calendar_creation: bool = Field(default=True, env="ENABLE_CALENDAR_CREATION")
    
    @field_validator('*', mode='before')
    @classmethod
    def strip_whitespace(cls, v):
        """Strip whitespace from all string values."""
        if isinstance(v, str):
            return v.strip()
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def validate_settings() -> None:
    """Validate that all required settings are present."""
    required_fields = [
        "google_client_id",
        "google_client_secret", 
        "gmail_user_email",
        "boxing_gym_email"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field):
            missing_fields.append(field.upper())
    
    if missing_fields:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_fields)}. "
            "Please copy env.example to .env and fill in the required values."
        )
    
    # Validate LLM configuration
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when using OpenAI")
    
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")
