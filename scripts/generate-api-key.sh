#!/bin/bash

# Generate a secure API key and store it in Secret Manager

PROJECT_ID="boxing-gym-agent"

echo "🔐 Generating secure API key..."

# Generate a random 32-character API key
API_KEY=$(openssl rand -hex 32)

echo "✅ Generated API key: ${API_KEY:0:10}... (truncated for security)"
echo ""
echo "📝 To use this API key with curl:"
echo "   curl -H \"X-API-Key: $API_KEY\" https://your-service-url/status"
echo ""

# Ask if user wants to store in Secret Manager
read -p "Do you want to store this API key in Google Cloud Secret Manager? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "📦 Storing API key in Secret Manager..."
    
    # Check if secret exists
    if gcloud secrets describe api-key --project=$PROJECT_ID &>/dev/null; then
        echo "⚠️  Secret 'api-key' already exists. Creating new version..."
        echo -n "$API_KEY" | gcloud secrets versions add api-key --data-file=- --project=$PROJECT_ID
    else
        echo "Creating new secret 'api-key'..."
        echo -n "$API_KEY" | gcloud secrets create api-key --data-file=- --project=$PROJECT_ID
    fi
    
    echo "✅ API key stored in Secret Manager as 'api-key'"
    echo ""
    echo "📋 Next steps:"
    echo "1. Deploy your Cloud Run service with --set-secrets=API_KEY=api-key:latest"
    echo "2. Save your API key securely (you won't be able to retrieve it later)"
    echo "3. Use the API key in the X-API-Key header for all requests"
else
    echo "⚠️  API key NOT stored in Secret Manager"
    echo "💾 Save this API key securely:"
    echo ""
    echo "   $API_KEY"
    echo ""
fi

