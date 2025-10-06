#!/bin/bash

# Simple deployment script for Boxing Gym Agent
set -e

PROJECT_ID="boxing-gym-agent"
REGION="us-central1"
SERVICE_NAME="boxing-gym-agent"

echo "🚀 Deploying Boxing Gym Agent to Cloud Run..."

# Set project
gcloud config set project $PROJECT_ID

# Build and push image
echo "📦 Building and pushing image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run with minimal configuration
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 10 \
    --port 8080

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Health Check: $SERVICE_URL/health"
echo "📚 API Docs: $SERVICE_URL/docs"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed. Check the logs:"
    echo "gcloud run logs tail $SERVICE_NAME --region $REGION"
fi
