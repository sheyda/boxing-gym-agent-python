"""LLM service for intelligent email processing."""

import json
from typing import Dict, Any, Optional
from loguru import logger

from ..config.settings import settings
from ..models.email_models import EmailMetadata, EmailClassification, ClassDetails


class LLMService:
    """Service for LLM-based email processing."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self._setup_client()
    
    def _setup_client(self):
        """Set up the LLM client based on provider."""
        if self.provider == "openai":
            import openai
            openai.api_key = settings.openai_api_key
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def classify_email(self, email: EmailMetadata) -> EmailClassification:
        """Classify email and extract relevant information using LLM."""
        try:
            prompt = self._build_classification_prompt(email)
            
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            return self._parse_classification_response(response)
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            # Return a fallback classification
            return EmailClassification(
                email_type="other",
                confidence=0.0,
                action_required="none",
                reasoning=f"Error in classification: {str(e)}"
            )
    
    def _build_classification_prompt(self, email: EmailMetadata) -> str:
        """Build the prompt for email classification."""
        return f"""
You are an AI assistant that processes emails for a boxing gym automation system. 
Analyze the following email and classify it, then extract relevant information.

Email Details:
- Subject: {email.subject}
- From: {email.from_email}
- Date: {email.date}
- Snippet: {email.snippet}
- Body: {email.body[:2000]}...

Please analyze this email and respond with a JSON object containing:

1. email_type: One of ["registration_form", "confirmation", "cancellation", "waitlist", "other"]
2. confidence: A float between 0.0 and 1.0 indicating your confidence in the classification
3. class_details: If this is a class-related email, extract:
   - class_name: Name of the class
   - date: Date of the class (if mentioned)
   - time: Time of the class (if mentioned)
   - instructor: Instructor name (if mentioned)
   - location: Location (if mentioned)
   - class_type: Type of class (e.g., "boxing", "kickboxing", "fitness")
   - difficulty: Difficulty level (if mentioned)
   - duration_minutes: Duration in minutes (if mentioned)
   - equipment_needed: List of equipment needed (if mentioned)
   - notes: Any additional notes
4. action_required: One of ["register", "create_calendar", "cancel_event", "waitlist", "none"]
5. form_links: List of any form URLs found in the email
6. registration_url: Primary registration URL if found
7. reasoning: Brief explanation of your classification and reasoning

Focus on:
- Boxing gym class registrations and confirmations
- Class schedules and details
- Registration forms and links
- Confirmation emails with class details

Respond with valid JSON only, no additional text.
"""
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that processes emails for boxing gym automation. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_classification_response(self, response: str) -> EmailClassification:
        """Parse LLM response into EmailClassification object."""
        try:
            # Clean the response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            data = json.loads(response)
            
            # Extract class details if present
            class_details = None
            if "class_details" in data and data["class_details"]:
                class_data = data["class_details"]
                class_details = ClassDetails(
                    class_name=class_data.get("class_name"),
                    date=class_data.get("date"),
                    time=class_data.get("time"),
                    instructor=class_data.get("instructor"),
                    location=class_data.get("location"),
                    class_type=class_data.get("class_type"),
                    difficulty=class_data.get("difficulty"),
                    duration_minutes=class_data.get("duration_minutes"),
                    equipment_needed=class_data.get("equipment_needed", []),
                    notes=class_data.get("notes")
                )
            
            return EmailClassification(
                email_type=data.get("email_type", "other"),
                confidence=float(data.get("confidence", 0.0)),
                class_details=class_details,
                action_required=data.get("action_required", "none"),
                form_links=data.get("form_links", []),
                registration_url=data.get("registration_url"),
                reasoning=data.get("reasoning", "")
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.error(f"Response was: {response}")
            
            # Return fallback classification
            return EmailClassification(
                email_type="other",
                confidence=0.0,
                action_required="none",
                reasoning=f"Error parsing response: {str(e)}"
            )
    
    def extract_class_details(self, email: EmailMetadata) -> Optional[ClassDetails]:
        """Extract class details from email using LLM."""
        try:
            prompt = f"""
Extract class details from this boxing gym email:

Subject: {email.subject}
Body: {email.body[:1500]}...

Return a JSON object with:
- class_name: Name of the class
- date: Date of the class (YYYY-MM-DD format if possible)
- time: Time of the class (HH:MM format if possible)
- instructor: Instructor name
- location: Location/venue
- class_type: Type of class
- difficulty: Difficulty level
- duration_minutes: Duration in minutes
- equipment_needed: Array of equipment needed
- notes: Any additional notes

If any field is not found, use null. Return valid JSON only.
"""
            
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "anthropic":
                response = self._call_anthropic(prompt)
            
            data = json.loads(response.strip())
            return ClassDetails(**data)
            
        except Exception as e:
            logger.error(f"Error extracting class details: {e}")
            return None
