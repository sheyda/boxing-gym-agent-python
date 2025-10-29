#!/bin/bash

# Get Boxing Gym Agent service information
# This script helps you get the current service URL and other deployment info

set -e

PROJECT_ID="boxing-gym-agent"
REGION="us-central1"
SERVICE_NAME="boxing-gym-agent"

echo "🔍 Getting Boxing Gym Agent service information..."

# Check if configuration is updated
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Please update PROJECT_ID in this script"
    echo "   Edit the script and set PROJECT_ID to your actual project ID"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

echo "📋 Project: $PROJECT_ID"
echo "🌍 Region: $REGION"
echo "🏷️  Service: $SERVICE_NAME"
echo ""

# Get service URL
echo "🔗 Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' 2>/dev/null || echo "Service not found")

if [ "$SERVICE_URL" = "Service not found" ]; then
    echo "❌ Service not found. Make sure it's deployed first."
    echo "   Run: gcloud run services list --platform managed --region $REGION"
    exit 1
fi

echo "✅ Service URL: $SERVICE_URL"
echo ""

# Test health endpoint
echo "🏥 Testing health endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" || echo "Failed")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Service is healthy"
elif [ "$HEALTH_STATUS" = "Failed" ]; then
    echo "❌ Service is not responding"
else
    echo "⚠️  Service returned status: $HEALTH_STATUS"
fi

echo ""
echo "📊 Useful commands:"
echo "   • Health check: curl $SERVICE_URL/health"
echo "   • Manual email check: curl -X POST $SERVICE_URL/check-emails -H 'X-API-Key: YOUR_API_KEY'"
echo "   • View logs: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --limit=20"
echo ""
echo "🔧 To set up Cloud Scheduler, use this URL in setup-scheduler-complete.sh:"
echo "   SERVICE_URL=\"$SERVICE_URL\""
