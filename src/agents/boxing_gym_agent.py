"""Main Boxing Gym Agent with LLM-based email processing."""

import asyncio
import schedule
import time
from typing import Set, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from ..services.gmail_service import GmailService
from ..services.llm_service import LLMService
from ..services.calendar_service import CalendarService
from ..config.settings import settings, validate_settings
from ..models.email_models import ProcessedEmail, AgentStatus, ClassDetails


class BoxingGymAgent:
    """Main agent for processing boxing gym emails with LLM intelligence."""
    
    def __init__(self):
        self.gmail_service = GmailService()
        self.llm_service = LLMService()
        self.calendar_service: Optional[CalendarService] = None
        self.processed_emails: Set[str] = set()
        self.is_running = False
        self.status = AgentStatus(
            is_running=False,
            processed_emails_count=0,
            errors_count=0,
            successful_actions=0
        )
    
    async def initialize(self) -> None:
        """Initialize the agent with all required services."""
        try:
            # Validate settings
            validate_settings()
            
            # Authenticate with Gmail
            self.gmail_service.authenticate()
            
            # Initialize calendar service with Gmail credentials
            self.calendar_service = CalendarService(self.gmail_service.credentials)
            
            logger.info("Boxing Gym Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise
    
    async def start(self) -> None:
        """Start the agent monitoring loop."""
        if self.is_running:
            logger.warning("Agent is already running")
            return
        
        self.is_running = True
        self.status.is_running = True
        logger.info("Starting Boxing Gym Agent...")
        
        # Process existing emails first
        await self.process_existing_emails()
        
        # Set up periodic checking
        self._setup_scheduler()
        
        # Start the monitoring loop
        await self._run_monitoring_loop()
    
    def stop(self) -> None:
        """Stop the agent."""
        self.is_running = False
        self.status.is_running = False
        schedule.clear()
        logger.info("Boxing Gym Agent stopped")
    
    def _setup_scheduler(self) -> None:
        """Set up the periodic email checking schedule."""
        schedule.every(settings.check_interval_minutes).minutes.do(
            lambda: asyncio.create_task(self.check_for_new_emails())
        )
        logger.info(f"Scheduled email checking every {settings.check_interval_minutes} minutes")
    
    async def _run_monitoring_loop(self) -> None:
        """Run the main monitoring loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.status.errors_count += 1
                await asyncio.sleep(5)  # Wait before retrying
    
    async def process_existing_emails(self) -> None:
        """Process existing emails in the inbox."""
        try:
            logger.info("Processing existing emails...")
            messages = self.gmail_service.search_emails(max_results=settings.max_emails_per_check)
            
            for message in messages:
                await self.process_email(message['id'])
                
        except Exception as e:
            logger.error(f"Error processing existing emails: {e}")
            self.status.errors_count += 1
    
    async def check_for_new_emails(self) -> None:
        """Check for new emails and process them."""
        try:
            messages = self.gmail_service.search_emails(max_results=settings.max_emails_per_check)
            new_messages = [msg for msg in messages if msg['id'] not in self.processed_emails]
            
            if new_messages:
                logger.info(f"Found {len(new_messages)} new emails to process")
                
                for message in new_messages:
                    await self.process_email(message['id'])
            
            self.status.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking for new emails: {e}")
            self.status.errors_count += 1
    
    async def process_email(self, message_id: str) -> None:
        """Process a single email with LLM classification."""
        try:
            if message_id in self.processed_emails:
                return
            
            # Get email details
            email_metadata = self.gmail_service.get_email(message_id)
            logger.info(f"Processing email: {email_metadata.subject}")
            
            # Classify email using LLM
            classification = self.llm_service.classify_email(email_metadata)
            
            # Create processed email object
            processed_email = ProcessedEmail(
                metadata=email_metadata,
                classification=classification
            )
            
            # Process based on classification
            await self._handle_classified_email(processed_email)
            
            # Mark as processed
            self.processed_emails.add(message_id)
            self.status.processed_emails_count += 1
            processed_email.processed = True
            
            logger.info(f"Email {message_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing email {message_id}: {e}")
            self.status.errors_count += 1
    
    async def _handle_classified_email(self, processed_email: ProcessedEmail) -> None:
        """Handle email based on LLM classification."""
        classification = processed_email.classification
        
        # Check confidence threshold
        if classification.confidence < settings.confidence_threshold:
            logger.warning(f"Low confidence classification ({classification.confidence:.2f}): {classification.reasoning}")
            return
        
        logger.info(f"Email classified as: {classification.email_type} (confidence: {classification.confidence:.2f})")
        logger.info(f"Action required: {classification.action_required}")
        
        # Handle different email types
        if classification.email_type == "registration_form":
            await self._handle_registration_form(processed_email)
        elif classification.email_type == "confirmation":
            await self._handle_confirmation_email(processed_email)
        elif classification.email_type == "cancellation":
            await self._handle_cancellation_email(processed_email)
        elif classification.email_type == "waitlist":
            await self._handle_waitlist_email(processed_email)
        else:
            logger.info(f"No specific handling for email type: {classification.email_type}")
    
    async def _handle_registration_form(self, processed_email: ProcessedEmail) -> None:
        """Handle registration form emails."""
        classification = processed_email.classification
        
        logger.info(f"Found registration form: {processed_email.metadata.subject}")
        logger.info(f"Form links: {classification.form_links}")
        logger.info(f"Registration URL: {classification.registration_url}")
        
        if classification.class_details:
            logger.info("Class details extracted:", classification.class_details.dict())
        
        # Log form information for manual review
        logger.info("Registration form details logged for review")
        
        # Mark email as read
        self.gmail_service.mark_as_read(processed_email.metadata.id)
        
        # Future: Could implement automatic form submission here
        if settings.enable_auto_registration:
            logger.info("Auto-registration is enabled but not yet implemented")
    
    async def _handle_confirmation_email(self, processed_email: ProcessedEmail) -> None:
        """Handle confirmation emails, especially Google Forms confirmations."""
        classification = processed_email.classification
        
        logger.info(f"Found confirmation email: {processed_email.metadata.subject}")
        
        # Check if this is a Google Forms confirmation
        is_google_forms_confirmation = (
            "Thanks for filling out this form: Boxing Class Registration" in processed_email.metadata.subject
        )
        
        if is_google_forms_confirmation:
            logger.info("Processing Google Forms confirmation email")
            
            # If LLM didn't extract class details, try to extract them manually
            if not classification.class_details or not classification.class_details.class_name:
                logger.info("Attempting to extract class details from Google Forms confirmation")
                classification.class_details = await self._extract_google_forms_details(processed_email)
        
        if not classification.class_details:
            logger.warning("No class details found in confirmation email")
            return
        
        # Log extracted class details
        logger.info("Class details extracted:")
        logger.info(f"  - Class: {classification.class_details.class_name}")
        logger.info(f"  - Date: {classification.class_details.date}")
        logger.info(f"  - Time: {classification.class_details.time}")
        logger.info(f"  - Instructor: {classification.class_details.instructor}")
        logger.info(f"  - Location: {classification.class_details.location}")
        
        # Create calendar event if enabled
        if settings.enable_calendar_creation:
            try:
                event = self.calendar_service.create_class_event(
                    classification.class_details,
                    processed_email.metadata.id
                )
                
                if event:
                    logger.info(f"Created calendar event: {event['id']}")
                    logger.info(f"Event title: {event.get('summary', 'N/A')}")
                    logger.info(f"Event start: {event.get('start', {}).get('dateTime', 'N/A')}")
                    self.status.successful_actions += 1
                else:
                    logger.info("Calendar event already exists or creation skipped")
                    
            except Exception as e:
                logger.error(f"Error creating calendar event: {e}")
                self.status.errors_count += 1
        else:
            logger.info("Calendar creation is disabled - skipping event creation")
        
        # Mark email as read
        self.gmail_service.mark_as_read(processed_email.metadata.id)
    
    async def _extract_google_forms_details(self, processed_email: ProcessedEmail) -> Optional[ClassDetails]:
        """Extract class details from Google Forms confirmation email using LLM."""
        try:
            logger.info("Using LLM to extract class details from Google Forms confirmation")
            
            # Create a specialized prompt for Google Forms extraction
            prompt = f"""
You are an AI assistant that extracts class details from Google Forms confirmation emails.

Email Details:
- Subject: {processed_email.metadata.subject}
- Body: {processed_email.metadata.body}

This is a Google Forms confirmation email for a boxing class registration. Please extract the following information from the email body and respond with a JSON object:

{{
    "class_name": "Name of the class (e.g., 'Boxing Class', 'Kickboxing', 'Fitness Training')",
    "date": "Date in YYYY-MM-DD format",
    "time": "Time in HH:MM format",
    "instructor": "Instructor/coach name",
    "location": "Location/address",
    "class_type": "Type of class (e.g., 'boxing', 'kickboxing', 'fitness')",
    "difficulty": "Difficulty level if mentioned",
    "duration_minutes": "Duration in minutes if mentioned",
    "equipment_needed": ["List of equipment needed"],
    "notes": "Any additional notes"
}}

Look for:
- Class name in the form response
- Date and time information
- Instructor/coach name
- Location or address
- Any special instructions or notes

If any information is not available, use null for that field.

Respond with valid JSON only, no additional text.
"""
            
            # Use LLM to extract details
            if settings.llm_provider == "openai":
                response = self.llm_service.client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                llm_response = response.choices[0].message.content
            elif settings.llm_provider == "anthropic":
                response = self.llm_service.client.messages.create(
                    model=settings.llm_model,
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                llm_response = response.content[0].text
            else:
                raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
            
            # Parse the JSON response
            import json
            extracted_data = json.loads(llm_response)
            
            # Create ClassDetails object
            class_details = ClassDetails(
                class_name=extracted_data.get("class_name"),
                date=extracted_data.get("date"),
                time=extracted_data.get("time"),
                instructor=extracted_data.get("instructor"),
                location=extracted_data.get("location"),
                class_type=extracted_data.get("class_type"),
                difficulty=extracted_data.get("difficulty"),
                duration_minutes=extracted_data.get("duration_minutes"),
                equipment_needed=extracted_data.get("equipment_needed"),
                notes=extracted_data.get("notes")
            )
            
            logger.info("Successfully extracted class details from Google Forms confirmation")
            return class_details
            
        except Exception as e:
            logger.error(f"Error extracting Google Forms details: {e}")
            return None
    
    async def _handle_cancellation_email(self, processed_email: ProcessedEmail) -> None:
        """Handle cancellation emails."""
        classification = processed_email.classification
        
        logger.info(f"Found cancellation email: {processed_email.metadata.subject}")
        
        if classification.class_details:
            logger.info("Cancellation details:", classification.class_details.dict())
        
        # Future: Could implement automatic calendar event cancellation here
        logger.info("Cancellation email processed - manual calendar cleanup may be needed")
        
        # Mark email as read
        self.gmail_service.mark_as_read(processed_email.metadata.id)
    
    async def _handle_waitlist_email(self, processed_email: ProcessedEmail) -> None:
        """Handle waitlist emails."""
        classification = processed_email.classification
        
        logger.info(f"Found waitlist email: {processed_email.metadata.subject}")
        
        if classification.class_details:
            logger.info("Waitlist details:", classification.class_details.dict())
        
        # Future: Could implement waitlist management here
        logger.info("Waitlist email processed")
        
        # Mark email as read
        self.gmail_service.mark_as_read(processed_email.metadata.id)
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status
    
    def get_processed_emails_count(self) -> int:
        """Get count of processed emails."""
        return len(self.processed_emails)
    
    def get_processed_emails(self) -> Set[str]:
        """Get set of processed email IDs."""
        return self.processed_emails.copy()
