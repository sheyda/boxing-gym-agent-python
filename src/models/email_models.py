"""Pydantic models for email processing."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EmailMetadata(BaseModel):
    """Email metadata extracted from Gmail."""
    id: str
    thread_id: str
    subject: str
    from_email: str
    to_email: str
    date: datetime
    snippet: str
    body: str


class ClassDetails(BaseModel):
    """Class information extracted from emails."""
    class_name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    instructor: Optional[str] = None
    location: Optional[str] = None
    class_type: Optional[str] = None
    difficulty: Optional[str] = None
    duration_minutes: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    notes: Optional[str] = None


class EmailClassification(BaseModel):
    """LLM classification of email type and content."""
    email_type: str = Field(..., description="Type of email: registration_form, confirmation, cancellation, waitlist, other")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for classification")
    class_details: Optional[ClassDetails] = None
    action_required: str = Field(..., description="Action to take: register, create_calendar, cancel_event, waitlist, none")
    form_links: Optional[List[str]] = None
    registration_url: Optional[str] = None
    reasoning: str = Field(..., description="LLM reasoning for the classification")


class ProcessedEmail(BaseModel):
    """Complete processed email with classification and metadata."""
    metadata: EmailMetadata
    classification: EmailClassification
    processed_at: datetime = Field(default_factory=datetime.now)
    processed: bool = False


class CalendarEvent(BaseModel):
    """Calendar event details."""
    summary: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    reminders: Optional[Dict[str, Any]] = None
    source: Optional[Dict[str, str]] = None


class AgentStatus(BaseModel):
    """Agent status information."""
    is_running: bool
    processed_emails_count: int
    last_check: Optional[datetime] = None
    errors_count: int = 0
    successful_actions: int = 0
