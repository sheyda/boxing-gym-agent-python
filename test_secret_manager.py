#!/usr/bin/env python3
"""
Test script to verify Secret Manager integration.
This script tests whether secrets are loaded from Secret Manager or environment variables.
"""

import os
import json
from src.config.secret_manager import secret_manager
from src.config.settings import settings

def test_secret_loading():
    """Test how secrets are being loaded."""
    print("🔍 Testing Secret Manager Integration")
    print("=" * 50)
    
    # Test 1: Check if environment variables are set
    print("\n1. Environment Variables Check:")
    env_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'OPENAI_API_KEY',
        'GMAIL_USER_EMAIL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Show first 10 chars for security
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print(f"   ✅ {var}: {masked_value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Test 2: Check Secret Manager direct access
    print("\n2. Secret Manager Direct Access:")
    secret_names = [
        'google-client-id',
        'google-client-secret',
        'openai-api-key', 
        'gmail-user-email'
    ]
    
    for secret_name in secret_names:
        try:
            value = secret_manager.get_secret(secret_name)
            if value:
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   ✅ {secret_name}: {masked_value}")
            else:
                print(f"   ❌ {secret_name}: Empty or not found")
        except Exception as e:
            print(f"   ❌ {secret_name}: Error - {e}")
    
    # Test 3: Check settings object
    print("\n3. Settings Object Values:")
    settings_vars = [
        'google_client_id',
        'google_client_secret',
        'openai_api_key',
        'gmail_user_email'
    ]
    
    for var in settings_vars:
        try:
            value = getattr(settings, var, None)
            if value:
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ❌ {var}: Not set")
        except Exception as e:
            print(f"   ❌ {var}: Error - {e}")
    
    # Test 4: Check Gmail tokens specifically
    print("\n4. Gmail Tokens Check:")
    try:
        tokens = secret_manager.get_secret("gmail-tokens")
        if tokens:
            # Try to parse as JSON
            token_data = json.loads(tokens)
            if 'token' in token_data:
                print(f"   ✅ Gmail tokens: Found (token length: {len(token_data['token'])})")
            else:
                print(f"   ⚠️  Gmail tokens: Found but no 'token' field")
        else:
            print(f"   ❌ Gmail tokens: Not found")
    except Exception as e:
        print(f"   ❌ Gmail tokens: Error - {e}")
    
    # Test 5: Configuration source analysis
    print("\n5. Configuration Source Analysis:")
    print("   Checking if values match between env vars and Secret Manager...")
    
    for var, secret_name in zip(env_vars, secret_names):
        env_value = os.getenv(var)
        secret_value = secret_manager.get_secret(secret_name)
        
        if env_value and secret_value:
            if env_value == secret_value:
                print(f"   ⚠️  {var}: Same value in both env and Secret Manager")
            else:
                print(f"   ✅ {var}: Different values (using Secret Manager)")
        elif secret_value and not env_value:
            print(f"   ✅ {var}: Only in Secret Manager (correct)")
        elif env_value and not secret_value:
            print(f"   ⚠️  {var}: Only in environment (fallback)")
        else:
            print(f"   ❌ {var}: Not found in either")

if __name__ == "__main__":
    test_secret_loading()
