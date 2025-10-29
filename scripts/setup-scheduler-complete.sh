#!/bin/bash

# Complete Cloud Scheduler Setup for Boxing Gym Agent
# This script sets up everything needed for the agent to run every 5 minutes

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="boxing-gym-agent"
REGION="us-central1"
SERVICE_NAME="boxing-gym-agent"
SERVICE_URL="https://boxing-gym-agent-k3bpullv6q-uc.a.run.app"

echo "🚀 Setting up Cloud Scheduler for Boxing Gym Agent..."
echo "⚠️  Please update the configuration variables in this script first!"

# Check if configuration is updated
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Please update PROJECT_ID in this script"
    exit 1
fi

if [ "$SERVICE_URL" = "https://your-service-url.run.app" ]; then
    echo "❌ Please update SERVICE_URL in this script"
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable run.googleapis.com

# Generate API key if it doesn't exist
echo "🔑 Checking for API key..."
API_KEY=$(gcloud secrets versions access latest --secret="api-key" 2>/dev/null || echo "")

if [ -z "$API_KEY" ]; then
    echo "🔑 Generating new API key..."
    API_KEY=$(openssl rand -hex 32)
    
    # Store in Secret Manager
    echo -n "$API_KEY" | gcloud secrets create api-key --data-file=- 2>/dev/null || \
    echo -n "$API_KEY" | gcloud secrets versions add api-key --data-file=-
    
    echo "✅ API key generated and stored in Secret Manager"
else
    echo "✅ Using existing API key from Secret Manager"
fi

# Check if scheduler job already exists
echo "🔍 Checking for existing scheduler job..."
if gcloud scheduler jobs describe boxing-gym-agent-check >/dev/null 2>&1; then
    echo "⚠️  Scheduler job already exists. Updating..."
    gcloud scheduler jobs update http boxing-gym-agent-check \
        --schedule="*/5 * * * *" \
        --uri="$SERVICE_URL/check-emails" \
        --http-method=POST \
        --headers="X-API-Key=$API_KEY" \
        --time-zone="America/Los_Angeles" \
        --description="Check for new boxing gym emails every 5 minutes" \
        --max-retry-attempts=3 \
        --max-retry-duration=300s
else
    echo "📅 Creating new Cloud Scheduler job..."
    gcloud scheduler jobs create http boxing-gym-agent-check \
        --schedule="*/5 * * * *" \
        --uri="$SERVICE_URL/check-emails" \
        --http-method=POST \
        --headers="X-API-Key=$API_KEY" \
        --time-zone="America/Los_Angeles" \
        --description="Check for new boxing gym emails every 5 minutes" \
        --max-retry-attempts=3 \
        --max-retry-duration=300s
fi

echo "✅ Cloud Scheduler job created/updated successfully!"

# Test the job
echo "🧪 Testing the scheduler job..."
gcloud scheduler jobs run boxing-gym-agent-check

echo ""
echo "🎉 Setup complete! Your agent will now:"
echo "   • Check for emails every 5 minutes automatically"
echo "   • Run on Cloud Run (serverless)"
echo "   • Scale to zero when not in use"
echo ""
echo "📊 Monitor your agent:"
echo "   • View logs: gcloud logging read 'resource.type=cloud_run_revision' --limit=50"
echo "   • Check status: curl $SERVICE_URL/health"
echo "   • Manual trigger: curl -X POST $SERVICE_URL/check-emails -H 'X-API-Key: $API_KEY'"
echo ""
echo "🔧 To update the schedule, run this script again with new values."
