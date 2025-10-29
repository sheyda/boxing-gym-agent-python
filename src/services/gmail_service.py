"""Gmail API service for email operations."""

import base64
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger

from ..config.settings import settings
from ..models.email_models import EmailMetadata


class GmailService:
    """Service for Gmail API operations."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/calendar',  # Full calendar access
    ]
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    def authenticate(self, token_file: str = "tokens.json") -> None:
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Try to load credentials from Secret Manager first
        try:
            from ..config.secret_manager import secret_manager
            tokens_json = secret_manager.get_secret("gmail-tokens")
            creds = Credentials.from_authorized_user_info(
                json.loads(tokens_json), self.SCOPES
            )
            logger.info("Loaded credentials from Secret Manager")
        except Exception as e:
            logger.info(f"Could not load credentials from Secret Manager: {e}")
            
            # Fallback to local file
            try:
                with open(token_file, 'r') as token:
                    creds = Credentials.from_authorized_user_info(
                        json.load(token), self.SCOPES
                    )
                logger.info("Loaded credentials from local file")
            except FileNotFoundError:
                logger.info("No existing token file found")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": settings.google_client_id,
                            "client_secret": settings.google_client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [settings.google_redirect_uri]
                        }
                    },
                    self.SCOPES
                )
                creds = flow.run_local_server(port=8080)
            
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail authentication successful")
    
    def get_auth_url(self) -> str:
        """Get authorization URL for OAuth2 flow."""
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.google_redirect_uri]
                }
            },
            self.SCOPES
        )
        return flow.authorization_url()[0]
    
    def search_emails(self, query: Optional[str] = None, max_results: int = 10) -> List[Dict[str, str]]:
        """Search for emails matching the query."""
        if not self.service:
            raise RuntimeError("Gmail service not authenticated")
        
        query = query or settings.gmail_query
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails matching query: {query}")
            return messages
            
        except HttpError as error:
            logger.error(f"Error searching emails: {error}")
            raise
    
    def get_email(self, message_id: str) -> EmailMetadata:
        """Get email details by message ID."""
        if not self.service:
            raise RuntimeError("Gmail service not authenticated")
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return self._parse_email(message)
            
        except HttpError as error:
            logger.error(f"Error getting email {message_id}: {error}")
            raise
    
    def mark_as_read(self, message_id: str) -> None:
        """Mark email as read."""
        if not self.service:
            raise RuntimeError("Gmail service not authenticated")
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"Marked email {message_id} as read")
            
        except HttpError as error:
            logger.error(f"Error marking email as read: {error}")
            raise
    
    def mark_as_processed(self, message_id: str, label_name: str = "boxing-gym-processed") -> None:
        """Mark an email as processed by adding a Gmail label."""
        if not self.service:
            raise RuntimeError("Gmail service not authenticated")
        
        try:
            # Get or create the label
            label_id = self._get_or_create_label(label_name)
            
            # Add label to the message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            logger.info(f"Marked email {message_id} as processed with label '{label_name}'")
        except HttpError as error:
            logger.error(f"Error marking email {message_id} as processed: {error}")
    
    def _get_or_create_label(self, label_name: str) -> str:
        """Get or create a Gmail label and return its ID."""
        if not self.service:
            raise RuntimeError("Gmail service not authenticated")
        
        try:
            # Try to find existing label
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'] == label_name:
                    logger.debug(f"Found existing label: {label_name}")
                    return label['id']
            
            # Create new label if not found
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            logger.info(f"Created new label: {label_name}")
            return created_label['id']
            
        except HttpError as error:
            logger.error(f"Error getting or creating label: {error}")
            raise
    
    def _parse_email(self, message: Dict[str, Any]) -> EmailMetadata:
        """Parse Gmail message into EmailMetadata."""
        headers = message['payload'].get('headers', [])
        
        # Extract headers
        header_dict = {h['name'].lower(): h['value'] for h in headers}
        
        subject = header_dict.get('subject', '')
        from_email = header_dict.get('from', '')
        to_email = header_dict.get('to', '')
        date_str = header_dict.get('date', '')
        
        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            date = datetime.now()
        
        # Extract body
        body = self._extract_body(message['payload'])
        
        return EmailMetadata(
            id=message['id'],
            thread_id=message['threadId'],
            subject=subject,
            from_email=from_email,
            to_email=to_email,
            date=date,
            snippet=message.get('snippet', ''),
            body=body
        )
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload."""
        body = ""
        
        if 'body' in payload and 'data' in payload['body']:
            # Single part message
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        elif 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
        
        return body
