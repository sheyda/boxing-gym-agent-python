#!/bin/bash

# Pre-commit hook to check for secrets
# Install with: ln -s ../../pre-commit-hook.sh .git/hooks/pre-commit

echo "🔍 Checking for secrets in staged files..."

# Check for common secret patterns
SECRET_PATTERNS=(
    "sk-proj-[a-zA-Z0-9_-]+"       # OpenAI API keys (new format)
    "sk-[a-zA-Z0-9]{20,}"          # OpenAI API keys (legacy format)
    "sk-ant-[a-zA-Z0-9_-]+"        # Anthropic API keys
    "GOCSPX-[a-zA-Z0-9_-]+"        # Google OAuth2 client secrets
    "ya29\.[a-zA-Z0-9_-]+"         # Gmail OAuth2 tokens
    "[0-9]+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com"  # Google OAuth2 client IDs
)

FOUND_SECRETS=false

# Files to ignore during secret scan (documentation files with examples)
IGNORE_FILES=(
    "DEPLOYMENT_GUIDE.md"
    "SECURITY_CLEANUP_SUMMARY.md" 
    "SECURITY.md"
    "GITHUB_ACTIONS_SETUP.md"
    "SECRET_MANAGER_CLEANUP.md"
)

# Convert ignore files to a grep-friendly regex
IGNORE_REGEX=$(printf "|%s" "${IGNORE_FILES[@]}")
IGNORE_REGEX=${IGNORE_REGEX:1} # Remove leading '|'

for pattern in "${SECRET_PATTERNS[@]}"; do
    if git diff --cached --name-only | grep -Ev "$IGNORE_REGEX" | xargs grep -lE "$pattern" 2>/dev/null; then
        echo "❌ Found potential secret matching pattern: $pattern"
        FOUND_SECRETS=true
    fi
done

if [ "$FOUND_SECRETS" = true ]; then
    echo ""
    echo "🚨 SECURITY WARNING: Potential secrets detected in staged files!"
    echo "Please remove or sanitize these secrets before committing."
    echo ""
    echo "Files with secrets should be:"
    echo "- Added to .gitignore"
    echo "- Use template files (.example) for version control"
    echo "- Store actual secrets in environment variables or Secret Manager"
    echo ""
    echo "See SECURITY.md for more information."
    exit 1
fi

echo "✅ No secrets detected in staged files."
exit 0