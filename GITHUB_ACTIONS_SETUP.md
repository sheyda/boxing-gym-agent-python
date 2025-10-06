# 🚀 GitHub Actions CI/CD Setup Guide

This guide explains how to set up automatic deployments using GitHub Actions for the Boxing Gym Agent.

## 📋 Prerequisites

- ✅ GitHub repository created
- ✅ Google Cloud project set up
- ✅ Service account created (`github-actions-sa`)
- ✅ Service account key generated (`github-actions-key.json`)

## 🔐 Step 1: Add GitHub Secret

1. **Go to your GitHub repository**: https://github.com/sheyda/boxing-gym-agent-python
2. **Navigate to Settings**: Repository Settings → Secrets and variables → Actions
3. **Create new secret**:
   - Click "New repository secret"
   - **Name**: `GCP_SA_KEY`
   - **Value**: Copy the entire content of `github-actions-key.json`
4. **Save the secret**

## 🔧 Step 2: Verify Workflow File

The workflow file is already created at `.github/workflows/deploy.yml` and includes:

- **Testing**: Python setup, dependency installation, linting
- **Building**: Docker image creation and tagging
- **Deploying**: Automatic deployment to Cloud Run
- **Health Check**: Service verification after deployment

## 🎯 Step 3: Test the Workflow

### Option A: Push to Master (Triggers Deployment)
```bash
git add .
git commit -m "Add GitHub Actions CI/CD workflow"
git push origin master
```

### Option B: Create Pull Request (Triggers Testing Only)
```bash
git checkout -b feature/test-ci-cd
git add .
git commit -m "Test GitHub Actions workflow"
git push origin feature/test-ci-cd
# Then create a PR on GitHub
```

## 📊 Workflow Details

### Triggers
- **Push to master/main**: Full CI/CD pipeline (test → build → deploy)
- **Pull requests**: Testing and building only (no deployment)

### Jobs

#### 1. Test Job
- Sets up Python 3.10
- Installs dependencies
- Runs tests (when available)
- Runs linting (when configured)

#### 2. Build and Deploy Job
- **Only runs on master/main branch**
- Authenticates with Google Cloud
- Builds Docker image
- Pushes to Google Container Registry
- Deploys to Cloud Run with:
  - Secrets from Secret Manager
  - Environment variables for configuration
  - Proper service account permissions

### Environment Variables
The deployment uses the hybrid approach:
- **Secrets**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OPENAI_API_KEY`, `GMAIL_TOKENS`, `GMAIL_USER_EMAIL`
- **Environment Variables**: All configuration values (timeouts, log levels, etc.)

## 🔍 Monitoring

### GitHub Actions Tab
1. Go to your repository on GitHub
2. Click the "Actions" tab
3. View workflow runs and logs

### Cloud Run Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to Cloud Run
3. View your deployed service

## 🛠️ Customization

### Adding Tests
Uncomment and modify the test section in `.github/workflows/deploy.yml`:
```yaml
- name: Run tests
  run: |
    python -m pytest tests/ -v
```

### Adding Linting
Uncomment and modify the linting section:
```yaml
- name: Lint code
  run: |
    pip install flake8 black
    flake8 src/
    black --check src/
```

### Environment-Specific Deployments
You can create separate workflows for different environments:
- `.github/workflows/deploy-staging.yml` - Deploy to staging
- `.github/workflows/deploy-production.yml` - Deploy to production

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify `GCP_SA_KEY` secret is correctly set
   - Check service account permissions

2. **Build Failed**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt

3. **Deployment Failed**
   - Check Cloud Run service account permissions
   - Verify Secret Manager secrets exist

4. **Health Check Failed**
   - Check application logs in Cloud Run
   - Verify the `/health` endpoint is working

### Debug Commands
```bash
# Check service account permissions
gcloud projects get-iam-policy boxing-gym-agent

# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --limit=50

# Test deployment manually
gcloud run deploy boxing-gym-agent --image gcr.io/boxing-gym-agent/boxing-gym-agent:latest
```

## 🎉 Success!

Once set up, every push to master will automatically:
1. ✅ Run tests
2. ✅ Build Docker image
3. ✅ Deploy to Cloud Run
4. ✅ Verify deployment health

Your Boxing Gym Agent will be automatically deployed with every successful build! 🚀

---

**Next Steps**: Push a commit to master to trigger your first automatic deployment!
