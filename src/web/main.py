"""Web interface for the Boxing Gym Agent on Cloud Run."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from src.agents.boxing_gym_agent import BoxingGymAgent
from src.config.settings import validate_settings
from src.models.email_models import AgentStatus


# Global agent instance
agent: BoxingGymAgent = None
app = FastAPI(
    title="Boxing Gym Agent",
    description="LLM-powered email automation for boxing gym class management",
    version="1.0.0"
)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    agent_running: bool
    processed_emails: int


class ProcessEmailRequest(BaseModel):
    """Request model for manual email processing."""
    message_id: str


class AgentResponse(BaseModel):
    """Agent status response model."""
    status: AgentStatus
    processed_emails_count: int
    uptime: str


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    try:
        print("Boxing Gym Agent web service starting...")
        
        # Validate settings
        validate_settings()
        
        # Initialize agent
        agent = BoxingGymAgent()
        await agent.initialize()
        
        # Start agent in background
        asyncio.create_task(agent.start())
        
        print("Boxing Gym Agent started successfully")
        
    except Exception as e:
        print(f"Error starting agent: {e}")
        # Don't raise to allow container to start, but log the error
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global agent
    if agent:
        agent.stop()
        print("Boxing Gym Agent stopped")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Boxing Gym Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cloud Run."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        agent_running=agent.is_running,
        processed_emails=agent.get_processed_emails_count()
    )


@app.get("/status", response_model=AgentResponse)
async def get_agent_status():
    """Get detailed agent status."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    status = agent.get_status()
    processed_count = agent.get_processed_emails_count()
    
    # Calculate uptime (simplified)
    uptime = "Unknown"  # Could be enhanced with start time tracking
    
    return AgentResponse(
        status=status,
        processed_emails_count=processed_count,
        uptime=uptime
    )


@app.post("/process-email")
async def process_email_manual(request: ProcessEmailRequest, background_tasks: BackgroundTasks):
    """Manually trigger email processing."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Process email in background
        background_tasks.add_task(agent.process_email, request.message_id)
        
        return {
            "message": f"Email {request.message_id} queued for processing",
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")


@app.post("/check-emails")
async def check_emails_manual(background_tasks: BackgroundTasks):
    """Manually trigger email checking."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Check emails in background
        background_tasks.add_task(agent.check_for_new_emails)
        
        return {
            "message": "Email check queued",
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking emails: {str(e)}")


@app.get("/processed-emails")
async def get_processed_emails():
    """Get list of processed email IDs."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    processed_emails = list(agent.get_processed_emails())
    
    return {
        "processed_emails": processed_emails,
        "count": len(processed_emails)
    }


@app.post("/restart")
async def restart_agent():
    """Restart the agent."""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Stop current agent
        agent.stop()
        
        # Reinitialize
        agent = BoxingGymAgent()
        await agent.initialize()
        
        # Start in background
        asyncio.create_task(agent.start())
        
        return {
            "message": "Agent restarted successfully",
            "status": "restarted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restarting agent: {str(e)}")


@app.get("/logs")
async def get_recent_logs():
    """Get recent log entries (simplified)."""
    # This is a simplified version - in production you'd want to integrate
    # with Cloud Logging or a proper log aggregation service
    
    return {
        "message": "Log endpoint - integrate with Cloud Logging for full functionality",
        "logs": "Use Cloud Logging console to view detailed logs"
    }


@app.get("/debug/secrets")
async def debug_secrets():
    """Debug endpoint to check secret loading sources."""
    import os
    from src.config.secret_manager import secret_manager
    from src.config.settings import settings
    
    # Check environment variables
    env_vars = {
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GMAIL_USER_EMAIL': os.getenv('GMAIL_USER_EMAIL')
    }
    
    # Check Secret Manager
    secret_manager_vars = {}
    secret_names = ['google-client-id', 'google-client-secret', 'openai-api-key', 'gmail-user-email']
    for secret_name in secret_names:
        try:
            secret_manager_vars[secret_name] = secret_manager.get_secret(secret_name)
        except Exception as e:
            secret_manager_vars[secret_name] = f"Error: {e}"
    
    # Check settings object
    settings_vars = {
        'google_client_id': getattr(settings, 'google_client_id', None),
        'google_client_secret': getattr(settings, 'google_client_secret', None),
        'openai_api_key': getattr(settings, 'openai_api_key', None),
        'gmail_user_email': getattr(settings, 'gmail_user_email', None)
    }
    
    # Mask sensitive values
    def mask_value(value):
        if not value:
            return None
        if isinstance(value, str) and len(value) > 10:
            return value[:10] + "..."
        return value
    
    return {
        "environment_variables": {k: mask_value(v) for k, v in env_vars.items()},
        "secret_manager": {k: mask_value(v) for k, v in secret_manager_vars.items()},
        "settings_object": {k: mask_value(v) for k, v in settings_vars.items()},
        "analysis": {
            "using_secret_manager": any(secret_manager_vars.values()),
            "using_env_vars": any(env_vars.values()),
            "secret_manager_count": sum(1 for v in secret_manager_vars.values() if v and not str(v).startswith("Error")),
            "env_var_count": sum(1 for v in env_vars.values() if v)
        }
    }


if __name__ == "__main__":
    # For local development
    uvicorn.run(
        "src.web.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
