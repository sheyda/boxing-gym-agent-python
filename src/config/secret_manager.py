"""Secret Manager integration for secure configuration management."""

import os
from typing import Optional
from google.cloud import secretmanager
from loguru import logger


class SecretManagerConfig:
    """Configuration manager that reads secrets from Google Cloud Secret Manager."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize Secret Manager client."""
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "boxing-gym-agent")
        self.client = secretmanager.SecretManagerServiceClient()
        self._cache = {}
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> str:
        """Get a secret value from Secret Manager with caching."""
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]
        
        # First try to get from environment variable (for Cloud Run secrets)
        env_var_name = secret_name.upper().replace("-", "_")
        env_value = os.getenv(env_var_name)
        if env_value is not None:
            # Strip whitespace from environment variable
            secret_value = env_value.strip()
            self._cache[secret_name] = secret_value
            logger.debug(f"Retrieved secret from environment: {secret_name}")
            return secret_value
        
        try:
            # Build the resource name
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            
            # Access the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Decode the secret value and strip whitespace
            secret_value = response.payload.data.decode("UTF-8").strip()
            
            # Cache the value
            self._cache[secret_name] = secret_value
            
            logger.debug(f"Retrieved secret: {secret_name}")
            return secret_value
            
        except Exception as e:
            logger.warning(f"Failed to retrieve secret {secret_name}: {e}")
            if default is not None:
                logger.info(f"Using default value for {secret_name}")
                return default
            # If no default provided and secret doesn't exist, return empty string
            logger.info(f"No default provided for {secret_name}, returning empty string")
            return ""
    
    def get_boolean_secret(self, secret_name: str, default: bool = False) -> bool:
        """Get a boolean secret value."""
        value = self.get_secret(secret_name, str(default).lower())
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int_secret(self, secret_name: str, default: int = 0) -> int:
        """Get an integer secret value."""
        value = self.get_secret(secret_name, str(default))
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {secret_name}: {value}, using default: {default}")
            return default
    
    def get_float_secret(self, secret_name: str, default: float = 0.0) -> float:
        """Get a float secret value."""
        value = self.get_secret(secret_name, str(default))
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {secret_name}: {value}, using default: {default}")
            return default


# Global instance
secret_manager = SecretManagerConfig()
