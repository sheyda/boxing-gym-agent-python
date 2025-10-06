"""Main entry point for the Boxing Gym Agent."""

import asyncio
import signal
import sys
from pathlib import Path
from loguru import logger

from .agents.boxing_gym_agent import BoxingGymAgent
from .config.settings import validate_settings


class BoxingGymAgentApp:
    """Main application class for the Boxing Gym Agent."""
    
    def __init__(self):
        self.agent = BoxingGymAgent()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.agent.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Run the application."""
        try:
            logger.info("Starting Boxing Gym Agent Application...")
            
            # Validate settings first
            validate_settings()
            
            # Initialize the agent
            await self.agent.initialize()
            
            # Start the agent
            await self.agent.start()
            
            logger.info("Boxing Gym Agent is now running!")
            logger.info("Press Ctrl+C to stop the agent")
            
            # Keep the application running
            while self.agent.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)
        finally:
            self.agent.stop()


async def main():
    """Main function."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create and run the application
    app = BoxingGymAgentApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
