"""Example of extending the Boxing Gym Agent for custom use cases."""

import asyncio
from typing import Optional
from loguru import logger

from src.agents.boxing_gym_agent import BoxingGymAgent
from src.models.email_models import ProcessedEmail


class CustomBoxingGymAgent(BoxingGymAgent):
    """Custom agent with additional features for specific use cases."""
    
    def __init__(self):
        super().__init__()
        self.notification_service = None  # Could be email, SMS, etc.
        self.fitness_tracker = None       # Could integrate with fitness apps
    
    async def _handle_confirmation_email(self, processed_email: ProcessedEmail) -> None:
        """Enhanced confirmation handling with custom features."""
        # Call parent method first
        await super()._handle_confirmation_email(processed_email)
        
        # Add custom processing
        await self._send_class_reminder(processed_email)
        await self._update_fitness_tracker(processed_email)
        await self._log_class_attendance(processed_email)
    
    async def _handle_registration_form(self, processed_email: ProcessedEmail) -> None:
        """Enhanced registration form handling."""
        # Call parent method first
        await super()._handle_registration_form(processed_email)
        
        # Add custom processing
        await self._analyze_class_preferences(processed_email)
        await self._check_class_availability(processed_email)
    
    async def _send_class_reminder(self, processed_email: ProcessedEmail) -> None:
        """Send custom class reminder."""
        classification = processed_email.classification
        if classification.class_details:
            logger.info(f"Sending reminder for {classification.class_details.class_name}")
            # Implement your notification logic here
            # Could be email, SMS, push notification, etc.
    
    async def _update_fitness_tracker(self, processed_email: ProcessedEmail) -> None:
        """Update fitness tracking app."""
        classification = processed_email.classification
        if classification.class_details:
            logger.info("Updating fitness tracker with class details")
            # Implement fitness app integration here
            # Could be MyFitnessPal, Strava, Apple Health, etc.
    
    async def _log_class_attendance(self, processed_email: ProcessedEmail) -> None:
        """Log class attendance for tracking."""
        classification = processed_email.classification
        if classification.class_details:
            logger.info("Logging class attendance")
            # Implement attendance tracking here
            # Could be database, spreadsheet, etc.
    
    async def _analyze_class_preferences(self, processed_email: ProcessedEmail) -> None:
        """Analyze class preferences for recommendations."""
        classification = processed_email.classification
        if classification.class_details:
            logger.info("Analyzing class preferences")
            # Implement preference analysis here
            # Could use ML to recommend similar classes
    
    async def _check_class_availability(self, processed_email: ProcessedEmail) -> None:
        """Check if class has available spots."""
        classification = processed_email.classification
        if classification.class_details:
            logger.info("Checking class availability")
            # Implement availability checking here
            # Could scrape gym website or use API


class MultiGymAgent(BoxingGymAgent):
    """Agent that handles multiple gyms with different configurations."""
    
    def __init__(self):
        super().__init__()
        self.gym_configs = {
            "boxing_gym_a": {
                "email": "gym-a@example.com",
                "query": "from:gym-a@example.com",
                "calendar_id": "primary",
                "timezone": "America/New_York",
            },
            "boxing_gym_b": {
                "email": "gym-b@example.com", 
                "query": "from:gym-b@example.com",
                "calendar_id": "secondary",
                "timezone": "America/Los_Angeles",
            }
        }
    
    async def _handle_confirmation_email(self, processed_email: ProcessedEmail) -> None:
        """Handle confirmations with gym-specific logic."""
        # Determine which gym this email is from
        gym_config = self._identify_gym(processed_email.metadata.from_email)
        
        if gym_config:
            logger.info(f"Processing confirmation from {gym_config['email']}")
            # Apply gym-specific processing
            await self._apply_gym_specific_processing(processed_email, gym_config)
        
        # Call parent method
        await super()._handle_confirmation_email(processed_email)
    
    def _identify_gym(self, from_email: str) -> Optional[dict]:
        """Identify which gym an email is from."""
        for gym_name, config in self.gym_configs.items():
            if config["email"] in from_email:
                return config
        return None
    
    async def _apply_gym_specific_processing(self, processed_email: ProcessedEmail, gym_config: dict) -> None:
        """Apply gym-specific processing logic."""
        logger.info(f"Applying gym-specific processing for {gym_config['email']}")
        # Implement gym-specific logic here


class SmartSchedulingAgent(BoxingGymAgent):
    """Agent with intelligent scheduling capabilities."""
    
    def __init__(self):
        super().__init__()
        self.schedule_preferences = {
            "preferred_times": ["18:00", "19:00", "20:00"],
            "preferred_days": ["Monday", "Wednesday", "Friday"],
            "max_classes_per_week": 3,
        }
    
    async def _handle_registration_form(self, processed_email: ProcessedEmail) -> None:
        """Smart registration form handling."""
        classification = processed_email.classification
        
        if classification.class_details:
            # Check if class fits preferences
            if self._class_fits_preferences(classification.class_details):
                logger.info("Class fits preferences - proceeding with registration")
                # Could implement automatic registration here
            else:
                logger.info("Class doesn't fit preferences - logging for review")
                await self._log_preference_mismatch(processed_email)
        
        # Call parent method
        await super()._handle_registration_form(processed_email)
    
    def _class_fits_preferences(self, class_details) -> bool:
        """Check if class fits user preferences."""
        # Implement preference checking logic
        return True  # Simplified for example
    
    async def _log_preference_mismatch(self, processed_email: ProcessedEmail) -> None:
        """Log classes that don't fit preferences."""
        logger.info("Logging preference mismatch for manual review")


# Example usage
async def main():
    """Example of running a custom agent."""
    # Create custom agent
    agent = CustomBoxingGymAgent()
    
    # Initialize and start
    await agent.initialize()
    await agent.start()
    
    # Keep running
    try:
        while agent.is_running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
