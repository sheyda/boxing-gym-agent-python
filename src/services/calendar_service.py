"""Google Calendar service for event management."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger

from ..config.settings import settings
from ..models.email_models import ClassDetails, CalendarEvent


class CalendarService:
    """Service for Google Calendar operations."""
    
    def __init__(self, credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def create_class_event(self, class_details: ClassDetails, email_id: str) -> Optional[Dict[str, Any]]:
        """Create a calendar event for a boxing class."""
        try:
            event_details = self._build_event_details(class_details, email_id)
            
            # Check if event already exists
            if self._event_exists(event_details):
                logger.info("Calendar event already exists for this class")
                return None
            
            event = self.service.events().insert(
                calendarId=settings.calendar_id,
                body=event_details
            ).execute()
            
            logger.info(f"Created calendar event: {event['id']}")
            return event
            
        except HttpError as error:
            logger.error(f"Error creating calendar event: {error}")
            raise
    
    def _build_event_details(self, class_details: ClassDetails, email_id: str) -> Dict[str, Any]:
        """Build calendar event details from class information."""
        # Parse start time
        start_time = self._parse_class_time(class_details)
        end_time = start_time + timedelta(minutes=class_details.duration_minutes or settings.event_duration_minutes)
        
        # Build event summary
        summary = f"{class_details.class_name or 'Boxing Class'} - {settings.boxing_gym_name}"
        
        # Build event description
        description = self._build_event_description(class_details, email_id)
        
        # Build location
        location = class_details.location or settings.boxing_gym_name
        
        return {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': settings.timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': settings.timezone,
            },
            'location': location,
            'attendees': [
                {
                    'email': settings.gmail_user_email,
                    'responseStatus': 'accepted',
                }
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
            # Note: Removed source URL as gmail:// format is not supported by Calendar API
            # The email ID is included in the description instead
        }
    
    def _build_event_description(self, class_details: ClassDetails, email_id: str) -> str:
        """Build event description from class details."""
        description_parts = [
            "Boxing class registration confirmed.",
            "",
        ]
        
        if class_details.instructor:
            description_parts.append(f"Instructor: {class_details.instructor}")
        
        if class_details.class_type:
            description_parts.append(f"Class Type: {class_details.class_type}")
        
        if class_details.difficulty:
            description_parts.append(f"Difficulty: {class_details.difficulty}")
        
        if class_details.equipment_needed:
            description_parts.append(f"Equipment: {', '.join(class_details.equipment_needed)}")
        
        if class_details.notes:
            description_parts.append(f"Notes: {class_details.notes}")
        
        description_parts.extend([
            "",
            f"Registered via Boxing Gym Agent",
            f"Email ID: {email_id}",
        ])
        
        return "\n".join(description_parts)
    
    def _parse_class_time(self, class_details: ClassDetails) -> datetime:
        """Parse class date and time into datetime object."""
        try:
            # Parse date
            if class_details.date:
                date_str = class_details.date.strip()
                
                if '/' in date_str:
                    # MM/DD/YYYY format
                    month, day, year = date_str.split('/')
                    date_obj = datetime(int(year), int(month), int(day))
                elif '-' in date_str:
                    # YYYY-MM-DD format
                    date_obj = datetime.fromisoformat(date_str)
                elif ',' in date_str and any(month in date_str for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                    # "Friday, October 10" format
                    try:
                        # Extract month and day from "Friday, October 10"
                        parts = date_str.split(',')
                        if len(parts) >= 2:
                            month_day = parts[1].strip()
                            month_name, day = month_day.split()
                            month_num = {
                                'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                            }.get(month_name, 1)
                            # Assume 2024 for boxing classes (current year)
                            year = 2024
                            date_obj = datetime(year, month_num, int(day))
                        else:
                            raise ValueError("Invalid date format")
                    except (ValueError, KeyError):
                        # Fallback to default
                        date_obj = datetime.now().date()
                else:
                    # Try to parse as ISO format
                    try:
                        date_obj = datetime.fromisoformat(date_str)
                    except ValueError:
                        # Fallback to today
                        date_obj = datetime.now().date()
            else:
                # Default to today
                date_obj = datetime.now().date()
            
            # Parse time
            if class_details.time:
                time_str = class_details.time.strip()
                
                # Handle various time formats
                if ':' in time_str:
                    if 'am' in time_str.lower() or 'pm' in time_str.lower():
                        # 12-hour format (e.g., "6:15pm", "6:15 PM")
                        time_part = time_str.replace('am', '').replace('pm', '').replace('AM', '').replace('PM', '').strip()
                        hour, minute = map(int, time_part.split(':'))
                        
                        if 'pm' in time_str.lower() and hour != 12:
                            hour += 12
                        elif 'am' in time_str.lower() and hour == 12:
                            hour = 0
                    else:
                        # 24-hour format (e.g., "18:15")
                        hour, minute = map(int, time_str.split(':'))
                    
                    # Combine date and time
                    return datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
                else:
                    # Just hour (e.g., "6" for 6 PM)
                    hour = int(time_str)
                    if hour < 12:  # Assume PM if hour < 12
                        hour += 12
                    return datetime.combine(date_obj, datetime.min.time().replace(hour=hour))
            else:
                # Default to 6 PM if no time specified
                return datetime.combine(date_obj, datetime.min.time().replace(hour=18))
                
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing class time: {e}")
            logger.error(f"Date: {class_details.date}, Time: {class_details.time}")
            # Default to tomorrow at 6 PM
            return datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _event_exists(self, event_details: Dict[str, Any]) -> bool:
        """Check if an event already exists for the same time and class."""
        try:
            start_time = datetime.fromisoformat(event_details['start']['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(event_details['end']['dateTime'].replace('Z', '+00:00'))
            
            events_result = self.service.events().list(
                calendarId=settings.calendar_id,
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check if any event has a similar summary
            class_name = event_details['summary'].split(' - ')[0]
            return any(class_name in event.get('summary', '') for event in events)
            
        except Exception as e:
            logger.error(f"Error checking for existing events: {e}")
            return False
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing calendar event."""
        try:
            event = self.service.events().update(
                calendarId=settings.calendar_id,
                eventId=event_id,
                body=updates
            ).execute()
            
            logger.info(f"Updated calendar event: {event_id}")
            return event
            
        except HttpError as error:
            logger.error(f"Error updating calendar event: {error}")
            raise
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event."""
        try:
            self.service.events().delete(
                calendarId=settings.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event: {event_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error deleting calendar event: {error}")
            return False
    
    def list_events(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """List events in a date range."""
        try:
            events_result = self.service.events().list(
                calendarId=settings.calendar_id,
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
            
        except HttpError as error:
            logger.error(f"Error listing events: {error}")
            return []
