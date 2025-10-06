# 🚀 Boxing Gym Agent - Cloud Run Deployment Guide

## Prerequisites Checklist

- [x] ✅ Google Cloud Project created (`boxing-gym-agent`)
- [x] ✅ Gmail API enabled
- [x] ✅ Google Calendar API enabled
- [x] ✅ OAuth2 credentials created and downloaded
- [x] ✅ gcloud CLI authenticated
- [ ] ⏳ LLM API key (OpenAI or Anthropic)
- [ ] ⏳ Environment variables configured

## Step-by-Step Deployment

### 1. Configure Environment Variables

Update your `.env` file with your actual values:

```env
# Google API Credentials (✅ Already set)
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET

# Gmail Configuration (Update these)
GMAIL_USER_EMAIL=your_actual_email@gmail.com
GMAIL_QUERY=from:your_boxing_gym@gmail.com subject:class registration

# Boxing Gym Configuration (Update these)
BOXING_GYM_EMAIL=your_boxing_gym@gmail.com
BOXING_GYM_NAME=Your Boxing Gym

# LLM Configuration (Choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-openai-key-here
LLM_MODEL=gpt-4-turbo-preview
```

### 2. Get LLM API Key

**Option A: OpenAI (Recommended)**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up/login → API Keys → Create new key
3. Add billing information
4. Copy the key (starts with `sk-`)

**Option B: Anthropic**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up/login → API Keys → Create new key
3. Add billing information
4. Copy the key (starts with `sk-ant-`)

### 3. Deploy to Cloud Run

Run the deployment script:

```bash
# Make sure you're in the project directory
cd /Users/sheyda/git/boxing-gym-agent-python

# Deploy to Cloud Run
./deploy.sh
```

The script will:
- Build the Docker image
- Push to Google Container Registry
- Deploy to Cloud Run
- Set up environment variables
- Test the deployment

### 4. Set Up Environment Variables in Cloud Run

After deployment, you need to set the environment variables in Cloud Run:

```bash
# Set your actual values
gcloud run services update boxing-gym-agent \
    --region us-central1 \
    --set-env-vars \
    GMAIL_USER_EMAIL=your_email@gmail.com,\
    BOXING_GYM_EMAIL=your_boxing_gym@gmail.com,\
    BOXING_GYM_NAME="Your Boxing Gym",\
    OPENAI_API_KEY=sk-your-actual-key-here,\
    LLM_PROVIDER=openai
```

### 5. Set Up Cloud Scheduler (Optional)

For periodic email checking, set up Cloud Scheduler:

```bash
# Create a job that runs every 5 minutes
gcloud scheduler jobs create http boxing-gym-agent-check \
    --schedule="*/5 * * * *" \
    --uri="https://your-service-url/check-emails" \
    --http-method=POST \
    --time-zone="America/New_York"
```

## Testing Your Deployment

### 1. Health Check
```bash
curl https://your-service-url/health
```

### 2. Check Status
```bash
curl https://your-service-url/status
```

### 3. View Logs
```bash
gcloud run logs tail boxing-gym-agent --region us-central1
```

## Monitoring and Management

### View Service Details
```bash
gcloud run services describe boxing-gym-agent --region us-central1
```

### Update Service
```bash
./deploy.sh
```

### View Logs
```bash
gcloud run logs tail boxing-gym-agent --region us-central1 --follow
```

## Cost Optimization

- **Cloud Run**: Pay only when processing emails (~$0.10-0.50/month)
- **LLM API**: ~$0.01-0.05 per email processed
- **Total estimated cost**: $5-20/month depending on email volume

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Errors**
   ```bash
   gcloud projects add-iam-policy-binding boxing-gym-agent \
       --member="user:your-email@gmail.com" \
       --role="roles/run.admin"
   ```

3. **Service Not Starting**
   - Check logs: `gcloud run logs tail boxing-gym-agent --region us-central1`
   - Verify environment variables are set correctly
   - Check API quotas and limits

### Getting Help

- View detailed logs in Cloud Console
- Check the `/docs` endpoint for API documentation
- Use the `/health` endpoint to verify service status

## Next Steps

1. **Set up monitoring** with Cloud Monitoring
2. **Configure alerts** for errors or high usage
3. **Set up backup** for OAuth tokens
4. **Add more gyms** by updating Gmail queries
5. **Extend functionality** using the examples in `/examples/`

## Security Notes

- Environment variables are encrypted in Cloud Run
- OAuth tokens are stored securely
- API keys are not logged
- Service runs in a secure container environment

---

🎉 **Your Boxing Gym Agent is now running in the cloud!**
