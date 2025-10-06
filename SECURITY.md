# 🔐 Security Guidelines

This document outlines security best practices for the Boxing Gym Agent project.

## 🚨 Important Security Notes

### Files Excluded from Git

The following files contain sensitive information and are **excluded from version control**:

- `tokens.json` - Gmail OAuth2 tokens
- `credentials.json` - Google OAuth2 client credentials
- `.env` - Environment variables with secrets
- `deploy-simple.sh` - Deployment script with hardcoded secrets
- `create-secrets.sh` - Secret creation script with API keys
- `deploy-with-secrets.sh` - Secret Manager deployment script

### Template Files

Use these template files as starting points:

- `deploy-simple.sh.example` - Template for deployment script
- `create-secrets.sh.example` - Template for secret creation
- `env.example` - Template for environment variables

## 🔑 Secret Management

### Production Deployment

**Use Google Cloud Secret Manager** for production deployments:

1. Create secrets using the template script:
   ```bash
   cp create-secrets.sh.example create-secrets.sh
   # Edit create-secrets.sh with your actual values
   chmod +x create-secrets.sh
   ./create-secrets.sh
   ```

2. Deploy using Secret Manager:
   ```bash
   cp deploy-with-secrets.sh.example deploy-with-secrets.sh
   # Edit deploy-with-secrets.sh with your actual values
   chmod +x deploy-with-secrets.sh
   ./deploy-with-secrets.sh
   ```

### Local Development

For local development, use environment variables:

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Fill in your actual values in `.env`

3. **Never commit `.env` to version control**

## 🛡️ Security Checklist

Before committing to Git:

- [ ] No API keys in code files
- [ ] No OAuth2 tokens in code files
- [ ] No email addresses in code files
- [ ] All secrets use environment variables or Secret Manager
- [ ] Template files use placeholder values
- [ ] `.gitignore` excludes sensitive files

## 🔍 Secret Detection

The project uses these patterns to detect potential secrets:

- OpenAI API keys: `sk-[a-zA-Z0-9]{20,}`
- Google OAuth2 client IDs: `[0-9]+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com`
- Google OAuth2 client secrets: `GOCSPX-[a-zA-Z0-9_-]+`
- Gmail OAuth2 tokens: `ya29\.[a-zA-Z0-9_-]+`

## 🚀 Deployment Security

### Cloud Run Service Account

The service uses a dedicated service account with minimal permissions:

- `roles/secretmanager.secretAccessor` - Read secrets from Secret Manager
- `roles/run.invoker` - Invoke Cloud Run services
- Gmail API access (via OAuth2)
- Google Calendar API access (via OAuth2)

### Network Security

- Cloud Run service is deployed with `--allow-unauthenticated` for simplicity
- Consider adding authentication for production use
- All API calls use HTTPS
- OAuth2 tokens are stored securely in Secret Manager

## 📝 Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** create a public issue
2. Email the maintainer directly
3. Include steps to reproduce the issue
4. Wait for confirmation before public disclosure

## 🔄 Regular Security Maintenance

- Rotate API keys regularly
- Monitor Cloud Logging for suspicious activity
- Keep dependencies updated
- Review and audit service account permissions
- Regularly check for exposed secrets in logs
