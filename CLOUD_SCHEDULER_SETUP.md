# Cloud Scheduler Setup Guide

This guide will help you set up Cloud Scheduler to make your Boxing Gym Agent run every 5 minutes automatically.

## 🎯 The Problem

Your agent wasn't catching this week's form because:
1. **Cloud Run scales to zero** - when there's no traffic, the service shuts down
2. **No persistent background processes** - the agent's 5-minute loop only runs while the container is active
3. **Wrong Gmail query** - you were looking for confirmation emails instead of registration forms

## 🚀 The Solution

Use **Cloud Scheduler** to trigger your agent every 5 minutes via HTTP requests.

## 📋 Prerequisites

- Your Boxing Gym Agent must be deployed to Cloud Run
- You need access to the Google Cloud Console
- `gcloud` CLI installed and authenticated

## 🛠️ Setup Steps

### Step 1: Get Your Service Information

First, let's get your current service URL:

```bash
# Update the script with your project ID
./scripts/get-service-info.sh
```

This will show you:
- Your service URL
- Health status
- Useful commands

### Step 2: Set Up Cloud Scheduler

1. **Update the configuration** in `scripts/setup-scheduler-complete.sh`:
   ```bash
   PROJECT_ID="your-actual-project-id"
   SERVICE_URL="https://your-actual-service-url.run.app"
   ```

2. **Run the setup script**:
   ```bash
   ./scripts/setup-scheduler-complete.sh
   ```

This script will:
- ✅ Enable required APIs
- ✅ Generate and store an API key
- ✅ Create a Cloud Scheduler job that runs every 5 minutes
- ✅ Test the setup

### Step 3: Update Your Gmail Query

Your current query looks for confirmation emails:
```
GMAIL_QUERY=subject:"Thanks for filling out this form: Boxing Class Registration" -label:boxing-gym-processed
```

**This is wrong!** You need to catch the actual registration forms, not the confirmations.

Update your `deploy-config.env`:
```bash
# OLD (looking for confirmations):
GMAIL_QUERY=subject:"Thanks for filling out this form: Boxing Class Registration" -label:boxing-gym-processed

# NEW (looking for registration forms):
GMAIL_QUERY=from:dreamlandboxing7@gmail.com (subject:registration OR subject:class OR subject:form) -label:boxing-gym-processed
```

### Step 4: Redeploy with Updated Query

After updating the Gmail query, redeploy your service:

```bash
# If using GitHub Actions, just push your changes
git add .
git commit -m "Fix Gmail query to catch registration forms"
git push

# Or deploy manually
gcloud run deploy boxing-gym-agent --source .
```

## 🧪 Testing

### Test the Scheduler Manually

```bash
# Trigger the scheduler job manually
gcloud scheduler jobs run boxing-gym-agent-check --location=us-central1

# Check the logs
gcloud logging read "resource.type=cloud_run_revision" --limit=20
```

### Test Email Processing

```bash
# Get your API key
API_KEY=$(gcloud secrets versions access latest --secret="api-key")

# Manually trigger email check
curl -X POST https://your-service-url.run.app/check-emails \
  -H "X-API-Key: $API_KEY"
```

## 📊 Monitoring

### View Scheduler Jobs

```bash
# List all scheduler jobs
gcloud scheduler jobs list --location=us-central1

# View job details
gcloud scheduler jobs describe boxing-gym-agent-check --location=us-central1
```

### View Service Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --limit=50

# Follow logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent"
```

### Check Service Health

```bash
# Health check
curl https://your-service-url.run.app/health

# Detailed status (requires API key)
curl https://your-service-url.run.app/status -H "X-API-Key: $API_KEY"
```

## 🔧 Troubleshooting

### Common Issues

1. **"Service not found"**
   - Make sure your service is deployed
   - Check the service name and region

2. **"Permission denied"**
   - Make sure you have Cloud Scheduler Admin role
   - Run: `gcloud auth login`

3. **"API key invalid"**
   - Check if the API key is stored in Secret Manager
   - Verify the service is using the same API key

4. **"No emails found"**
   - Check your Gmail query syntax
   - Make sure you're looking for the right email types
   - Test the query in Gmail directly

### Debug Commands

```bash
# Check if scheduler job exists
gcloud scheduler jobs describe boxing-gym-agent-check --location=us-central1

# Check service status
gcloud run services describe boxing-gym-agent --region=us-central1

# View all logs
gcloud logging read "resource.type=cloud_run_revision" --limit=100
```

## 🎉 Success!

Once set up, your agent will:
- ✅ Run every 5 minutes automatically
- ✅ Catch registration forms (not just confirmations)
- ✅ Scale to zero when not in use (cost-effective)
- ✅ Process emails with LLM intelligence
- ✅ Create calendar events automatically

## 📝 Next Steps

1. **Monitor the first few runs** to make sure it's working
2. **Check your calendar** for automatically created events
3. **Adjust the Gmail query** if needed based on your gym's email patterns
4. **Set up alerts** if you want notifications when forms are processed

Your Boxing Gym Agent will now catch this week's form and all future forms! 🥊
