# How to Refresh Gmail Tokens

Your Gmail tokens have expired and need to be refreshed. Follow these steps:

## 🔑 Step 1: Get OAuth2 Credentials

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/
   - Select your project: `boxing-gym-agent`

2. **Navigate to APIs & Services → Credentials**:
   - https://console.cloud.google.com/apis/credentials?project=boxing-gym-agent

3. **Download OAuth2 Client Credentials**:
   - Find your OAuth 2.0 Client ID (it should be listed under "OAuth 2.0 Client IDs")
   - Click on the client ID name
   - Click **"DOWNLOAD JSON"** button at the top
   - Save the file

4. **Rename and Move the File**:
   ```bash
   # Move the downloaded file to your project directory
   mv ~/Downloads/client_secret_*.json /Users/sheyda/git/boxing-gym-agent-python/credentials.json
   ```

## 🔄 Step 2: Run the Token Regeneration Script

```bash
cd /Users/sheyda/git/boxing-gym-agent-python
python regenerate_tokens.py
```

This will:
1. Open a browser window for Google authentication
2. Ask you to sign in with your Gmail account
3. Request permission to access Gmail and Calendar
4. Save the new tokens to `tokens.json`

## ☁️ Step 3: Update Secret Manager

Once you have the new `tokens.json`, update Secret Manager:

```bash
# Update the gmail-tokens secret
cat tokens.json | gcloud secrets versions add gmail-tokens --data-file=-
```

## 🚀 Step 4: Restart Cloud Run Service

The easiest way is to trigger a new deployment:

**Option 1: Via API (Quick)**
```bash
# Get your API key
API_KEY=$(gcloud secrets versions access latest --secret="api-key")

# Restart the agent
curl -X POST https://boxing-gym-agent-k3bpullv6q-uc.a.run.app/restart \
  -H "X-API-Key: $API_KEY"
```

**Option 2: Redeploy (More Reliable)**
```bash
# Push a change to trigger GitHub Actions deployment
git add .
git commit -m "Update Gmail tokens"
git push
```

**Option 3: Manual Cloud Run Update**
```bash
# Force a new revision
gcloud run services update boxing-gym-agent \
  --region us-central1 \
  --update-secrets=GMAIL_TOKENS=gmail-tokens:latest
```

## ✅ Step 5: Verify It's Working

Check the logs to confirm authentication is successful:

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --limit=10

# Look for "Gmail service authenticated" or similar success messages
# You should NOT see "Gmail service not authenticated" errors anymore
```

## 🧪 Step 6: Test Email Processing

```bash
# Get your API key
API_KEY=$(gcloud secrets versions access latest --secret="api-key")

# Trigger a manual email check
curl -X POST https://boxing-gym-agent-k3bpullv6q-uc.a.run.app/check-emails \
  -H "X-API-Key: $API_KEY"

# Check the logs to see if it worked
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --limit=5
```

## 🔍 Troubleshooting

### Issue: "credentials.json not found"
**Solution**: Make sure you downloaded and renamed the file correctly:
```bash
ls -la /Users/sheyda/git/boxing-gym-agent-python/credentials.json
```

### Issue: "Token still expired after refresh"
**Solution**: The tokens might have been revoked. Try:
1. Delete the old tokens: `rm tokens.json`
2. Run the regeneration script again: `python regenerate_tokens.py`
3. Make sure you authorize with the correct Gmail account

### Issue: "Permission denied" during OAuth flow
**Solution**: Make sure:
1. The Gmail API is enabled in your project
2. The OAuth consent screen is configured
3. Your email is added as a test user (if the app is in testing mode)

### Issue: "Browser doesn't open"
**Solution**: The script will print a URL. Copy and paste it into your browser manually.

## 📝 Quick Reference

```bash
# Full refresh process (copy-paste friendly)
cd /Users/sheyda/git/boxing-gym-agent-python

# 1. Make sure you have credentials.json
ls credentials.json

# 2. Regenerate tokens
python regenerate_tokens.py

# 3. Update Secret Manager
cat tokens.json | gcloud secrets versions add gmail-tokens --data-file=-

# 4. Restart the service
API_KEY=$(gcloud secrets versions access latest --secret="api-key")
curl -X POST https://boxing-gym-agent-k3bpullv6q-uc.a.run.app/restart -H "X-API-Key: $API_KEY"

# 5. Verify
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=boxing-gym-agent" --limit=5
```

## 🎉 Done!

Once the tokens are refreshed and the service is restarted, your agent will:
- ✅ Run every 5 minutes (already working)
- ✅ Check Gmail for confirmation emails
- ✅ Process emails with LLM
- ✅ Create calendar events automatically

Your agent should now catch this week's form and all future forms! 🥊
