#!/bin/bash

# Setup Cloud Scheduler for Boxing Gym Agent
# This script creates a Cloud Scheduler job that triggers the agent every 5 minutes

set -e

PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="boxing-gym-agent"
SERVICE_URL="https://your-service-url.run.app"

echo "🚀 Setting up Cloud Scheduler for Boxing Gym Agent..."

# Set project
gcloud config set project $PROJECT_ID

# Create Cloud Scheduler job
echo "📅 Creating Cloud Scheduler job..."
gcloud scheduler jobs create http boxing-gym-agent-check \
    --schedule="*/5 * * * *" \
    --uri="$SERVICE_URL/check-emails" \
    --http-method=POST \
    --headers="X-API-Key=YOUR_API_KEY" \
    --time-zone="America/Los_Angeles" \
    --description="Check for new boxing gym emails every 5 minutes" \
    --max-retry-attempts=3 \
    --max-retry-duration=300s

echo "✅ Cloud Scheduler job created successfully!"
echo "The agent will now check for emails every 5 minutes automatically."

# Optional: Test the job
echo "🧪 Testing the scheduler job..."
gcloud scheduler jobs run boxing-gym-agent-check

echo "🎉 Setup complete! Your agent will now run every 5 minutes."
