#!/bin/bash

# Boxing Gym Agent - Cloud Run Deployment Script
# This script builds and deploys the agent to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"boxing-gym-agent"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="boxing-gym-agent"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Boxing Gym Agent - Cloud Run Deployment${NC}"
echo "================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ Please set PROJECT_ID environment variable${NC}"
    echo "Example: export PROJECT_ID=my-boxing-gym-project"
    exit 1
fi

# Set the project
echo -e "${YELLOW}📋 Setting project to: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the image
echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
docker build -t $IMAGE_NAME .

echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "PROJECT_ID=$PROJECT_ID" \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo "================================================"
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}📊 Health Check: $SERVICE_URL/health${NC}"
echo -e "${GREEN}📚 API Docs: $SERVICE_URL/docs${NC}"
echo "================================================"

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
if curl -f -s "$SERVICE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed. Check the logs.${NC}"
    echo "View logs: gcloud run logs tail $SERVICE_NAME --region $REGION"
fi

echo -e "${GREEN}🎉 Boxing Gym Agent is now running on Cloud Run!${NC}"
echo ""
echo "Next steps:"
echo "1. Set up environment variables in Cloud Run console"
echo "2. Configure Cloud Scheduler for periodic execution"
echo "3. Set up monitoring and alerting"
echo ""
echo "View logs: gcloud run logs tail $SERVICE_NAME --region $REGION"
echo "Update service: ./deploy.sh"
