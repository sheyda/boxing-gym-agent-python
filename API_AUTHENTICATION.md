# 🔐 API Authentication

The Boxing Gym Agent API is protected with API key authentication to prevent unauthorized access.

## 🚨 Security Overview

### **Protected Endpoints** (Require `X-API-Key` header)
- `/status` - Agent status
- `/process-email` - Trigger email processing
- `/check-emails` - Trigger email check
- `/processed-emails` - List processed emails
- `/restart` - Restart agent
- `/logs` - View logs
- `/debug/secrets` - Debug endpoint

### **Public Endpoints** (No authentication required)
- `/` - Root info
- `/health` - Health check (required for Cloud Run)

## 🔑 Setting Up API Key

### Step 1: Generate API Key

Run the provided script to generate a secure random API key:

```bash
./scripts/generate-api-key.sh
```

This will:
1. Generate a cryptographically secure 64-character API key
2. Optionally store it in Google Cloud Secret Manager
3. Display the API key for you to save securely

### Step 2: Store API Key Securely

**Option A: Secret Manager (Recommended for Production)**
```bash
# The script will do this for you, or manually:
echo -n "your-api-key-here" | gcloud secrets create api-key \
  --data-file=- \
  --project=boxing-gym-agent
```

**Option B: Environment Variable (For Testing)**
```bash
export API_KEY="your-api-key-here"
```

### Step 3: Deploy with API Key

The GitHub Actions workflow automatically includes the API key from Secret Manager:
```yaml
--set-secrets="...,API_KEY=api-key:latest"
```

## 📝 Using the API

### With Authentication

```bash
# Get status
curl -H "X-API-Key: your-api-key-here" \
  https://your-service-url/status

# Trigger email check
curl -X POST \
  -H "X-API-Key: your-api-key-here" \
  https://your-service-url/check-emails

# Get processed emails
curl -H "X-API-Key: your-api-key-here" \
  https://your-service-url/processed-emails
```

### Without Authentication (Health Check Only)

```bash
# Health check - no API key needed
curl https://your-service-url/health
```

## ❌ Error Responses

### Missing API Key
```json
{
  "detail": "Invalid or missing API key. Include X-API-Key header."
}
```
**Status Code**: 403 Forbidden

### Invalid API Key
```json
{
  "detail": "Invalid or missing API key. Include X-API-Key header."
}
```
**Status Code**: 403 Forbidden

## 🔒 Security Best Practices

### ✅ DO
- Store API key in Secret Manager for production
- Use HTTPS for all API requests
- Rotate API keys periodically
- Keep API keys secret (don't commit to Git)
- Use environment-specific API keys (dev, staging, prod)

### ❌ DON'T
- Share API keys publicly
- Commit API keys to version control
- Use the same API key across environments
- Hardcode API keys in client applications
- Log API keys in plain text

## 🔄 Rotating API Keys

To rotate your API key:

1. Generate a new API key:
   ```bash
   ./scripts/generate-api-key.sh
   ```

2. Update Secret Manager with new key:
   ```bash
   echo -n "new-api-key" | gcloud secrets versions add api-key \
     --data-file=- \
     --project=boxing-gym-agent
   ```

3. Redeploy the service (GitHub Actions will pick up the new version)

4. Update any clients with the new API key

5. Test the new key works

6. Decommission old key

## 🆘 Troubleshooting

### "Invalid or missing API key"
- Check that you're including the `X-API-Key` header
- Verify the API key is correct (no extra spaces or newlines)
- Ensure Secret Manager has the `api-key` secret
- Check Cloud Run has access to the secret

### "Agent not initialized"
- This is a service error, not authentication
- The API key was valid, but the agent failed to start
- Check Cloud Run logs for startup errors

## 📚 Additional Resources

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager)
- [API Key Best Practices](https://cloud.google.com/endpoints/docs/openapi/when-why-api-key)

