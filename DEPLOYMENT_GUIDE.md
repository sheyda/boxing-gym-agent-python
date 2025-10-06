# 🚀 Boxing Gym Agent - Automated Deployment Guide

## Overview

The Boxing Gym Agent now uses **GitHub Actions** for fully automated CI/CD deployment to Google Cloud Run. Every push to the `master` branch automatically builds, tests, and deploys the application.

## Prerequisites Checklist

- [x] ✅ Google Cloud Project created (`boxing-gym-agent`)
- [x] ✅ Gmail API enabled
- [x] ✅ Google Calendar API enabled
- [x] ✅ OAuth2 credentials created and downloaded
- [x] ✅ GitHub repository created
- [x] ✅ GitHub Actions service account configured
- [x] ✅ Secrets stored in Google Cloud Secret Manager
- [x] ✅ GitHub repository secrets configured

## 🎯 Current Deployment Approach

### **Fully Automated CI/CD Pipeline**

```
Code Changes → Push to Master → GitHub Actions → Automatic Deployment
```

**What happens automatically:**
1. **Testing** - Runs tests and linting
2. **Building** - Creates Docker image
3. **Pushing** - Uploads to Artifact Registry
4. **Deploying** - Updates Cloud Run service
5. **Health Check** - Verifies deployment success

## 🔧 Initial Setup (One-time)

### 1. Configure Secrets in Google Cloud Secret Manager

Use the minimal secrets approach (recommended):

```bash
# Copy and edit the template
cp create-secrets-minimal.sh.example create-secrets-minimal.sh

# Edit with your actual values
nano create-secrets-minimal.sh

# Run to create secrets
chmod +x create-secrets-minimal.sh
./create-secrets-minimal.sh
```

**Required secrets:**
- `google-client-id` - Your Google OAuth2 client ID
- `google-client-secret` - Your Google OAuth2 client secret
- `openai-api-key` - Your OpenAI API key
- `gmail-tokens` - Gmail OAuth2 tokens (from `tokens.json`)
- `gmail-user-email` - Your Gmail address

### 2. Configure GitHub Repository Secrets

1. Go to your GitHub repository: `https://github.com/sheyda/boxing-gym-agent-python`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Create a new secret named `GCP_SA_KEY`
4. Copy the content of `github-actions-key.json` as the value
5. Save the secret

### 3. Authenticate Gmail API (One-time)

```bash
# Run the authentication script
python auth_gmail.py

# This will:
# - Open browser for Google OAuth2
# - Generate tokens.json
# - Upload tokens to Secret Manager
```

## 🚀 Deployment Process

### **Automatic Deployment (Recommended)**

Simply push to the `master` branch:

```bash
# Make your changes
git add .
git commit -m "Your changes"
git push origin master

# GitHub Actions automatically:
# ✅ Runs tests
# ✅ Builds Docker image  
# ✅ Deploys to Cloud Run
# ✅ Verifies deployment
```

### **Monitor Deployment**

1. **GitHub Actions**: https://github.com/sheyda/boxing-gym-agent-python/actions
2. **Cloud Run Console**: https://console.cloud.google.com/run
3. **Service URL**: Automatically deployed and updated

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe boxing-gym-agent --platform managed --region us-central1 --format 'value(status.url)' --project=boxing-gym-agent)

# Test health endpoint
curl $SERVICE_URL/health
```

### 2. Debug Secret Loading
```bash
# Check if secrets are loaded correctly
curl $SERVICE_URL/debug/secrets
```

### 3. Manual Email Check
```bash
# Trigger manual email processing
curl -X POST $SERVICE_URL/check-emails
```

### 4. View Logs
```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --project=boxing-gym-agent --limit=50 --format="table(timestamp,severity,textPayload)"
```

## 🔄 Development Workflow

### **For New Features:**
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test locally
python src/web/main.py

# Push to feature branch (triggers tests only)
git push origin feature/new-feature

# Create pull request (triggers tests)
# Merge to master (triggers full deployment)
```

### **For Hotfixes:**
```bash
# Make urgent changes
git add .
git commit -m "Hotfix: urgent issue"
git push origin master

# Automatic deployment in ~2-3 minutes
```

## 📊 Monitoring and Management

### **GitHub Actions Dashboard**
- View build status and logs
- Monitor deployment history
- Debug failed deployments

### **Cloud Run Console**
- Monitor service performance
- View request metrics
- Check resource usage

### **Cloud Logging**
- Search and filter logs
- Set up alerts
- Monitor errors

## 🛠️ Configuration Management

### **Secrets (Sensitive Data)**
- Stored in Google Cloud Secret Manager
- Automatically injected during deployment
- Rotated and managed centrally

### **Configuration (Non-sensitive)**
- Set via environment variables in GitHub Actions
- Includes timeouts, log levels, feature flags
- Version controlled in workflow file

### **Updating Configuration**
```bash
# Edit .github/workflows/deploy.yml
# Update environment variables section
# Push to master for automatic deployment
```

## 🔒 Security Features

- ✅ **No secrets in code** - All sensitive data in Secret Manager
- ✅ **Encrypted in transit** - HTTPS for all communications
- ✅ **Least privilege** - Minimal IAM permissions
- ✅ **Audit trail** - All secret access logged
- ✅ **Automatic rotation** - Secrets can be rotated without code changes

## 💰 Cost Optimization

- **Cloud Run**: Pay only when processing (~$0.10-0.50/month)
- **LLM API**: ~$0.01-0.05 per email processed
- **GitHub Actions**: Free for public repositories
- **Secret Manager**: ~$0.06 per secret per month
- **Total estimated cost**: $5-20/month depending on usage

## 🚨 Troubleshooting

### **Deployment Failures**

1. **Check GitHub Actions logs**
   - Go to Actions tab in GitHub
   - Click on failed workflow
   - Review error messages

2. **Common issues:**
   - Missing `GCP_SA_KEY` secret in GitHub
   - Insufficient IAM permissions
   - Secret Manager secrets not found
   - Docker build failures

### **Service Issues**

1. **Health check failures**
   ```bash
   curl $SERVICE_URL/health
   ```

2. **Secret loading issues**
   ```bash
   curl $SERVICE_URL/debug/secrets
   ```

3. **View detailed logs**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --project=boxing-gym-agent --limit=100
   ```

### **Authentication Issues**

1. **Gmail API authentication**
   ```bash
   # Re-run authentication
   python auth_gmail.py
   ```

2. **Service account permissions**
   ```bash
   # Check IAM permissions
   gcloud projects get-iam-policy boxing-gym-agent
   ```

## 🎯 Best Practices

### **Development**
- Use feature branches for new development
- Test locally before pushing
- Keep commits focused and descriptive
- Use pull requests for code review

### **Deployment**
- Monitor GitHub Actions for deployment status
- Check health endpoints after deployment
- Review logs for any issues
- Keep secrets updated in Secret Manager

### **Security**
- Never commit secrets to Git
- Use pre-commit hooks to prevent accidents
- Regularly rotate API keys
- Monitor secret access logs

## 📚 Alternative Deployment Methods

If you need manual deployment options, template files are available:

- `deploy-hybrid.sh.example` - Hybrid approach (secrets + env vars)
- `deploy-simple.sh.example` - Simple deployment with env vars
- `create-secrets-minimal.sh.example` - Minimal secret setup

## 🎉 Success!

Your Boxing Gym Agent is now running with:
- ✅ **Fully automated deployments**
- ✅ **Secure secret management**
- ✅ **Professional CI/CD pipeline**
- ✅ **Production-ready infrastructure**

**Next steps:**
1. Monitor the first few deployments
2. Set up Cloud Monitoring alerts
3. Configure additional gyms as needed
4. Extend functionality using the modular architecture

---

🚀 **Happy coding! Your agent will automatically deploy every time you push to master.**