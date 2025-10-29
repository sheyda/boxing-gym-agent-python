#!/usr/bin/env python3
"""
Script to regenerate OAuth2 tokens with updated scopes.
This is needed when we add new API scopes to the application.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Updated scopes including Calendar API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',  # Full calendar access
]

def regenerate_tokens():
    """Regenerate OAuth2 tokens with updated scopes."""
    creds = None
    
    # Check if we have existing tokens
    if os.path.exists('tokens.json'):
        print("Found existing tokens.json")
        try:
            creds = Credentials.from_authorized_user_file('tokens.json', SCOPES)
            print("Loaded existing credentials")
        except Exception as e:
            print(f"Error loading existing credentials: {e}")
            creds = None
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("Credentials refreshed successfully")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            print("Starting OAuth2 flow...")
            print("This will open a browser window for authentication.")
            print("Please make sure you have credentials.json in the current directory.")
            
            if not os.path.exists('credentials.json'):
                print("ERROR: credentials.json not found!")
                print("Please download your OAuth2 credentials from Google Cloud Console")
                print("and save them as 'credentials.json' in this directory.")
                return
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("OAuth2 flow completed successfully")
    
    # Save the credentials for the next run
    with open('tokens.json', 'w') as token:
        token.write(creds.to_json())
    print("Tokens saved to tokens.json")
    
    # Test the credentials with both Gmail and Calendar APIs
    print("\nTesting API access...")
    
    try:
        # Test Gmail API
        gmail_service = build('gmail', 'v1', credentials=creds)
        profile = gmail_service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail API: Connected as {profile.get('emailAddress')}")
    except Exception as e:
        print(f"❌ Gmail API: Error - {e}")
    
    try:
        # Test Calendar API
        calendar_service = build('calendar', 'v3', credentials=creds)
        calendar_list = calendar_service.calendarList().list().execute()
        print(f"✅ Calendar API: Connected, found {len(calendar_list.get('items', []))} calendars")
    except Exception as e:
        print(f"❌ Calendar API: Error - {e}")
    
    print("\n🎉 Token regeneration complete!")
    print("You can now upload the new tokens.json to Secret Manager:")
    print("gcloud secrets versions add gmail-tokens --data-file=tokens.json --project=boxing-gym-agent")

if __name__ == "__main__":
    regenerate_tokens()
