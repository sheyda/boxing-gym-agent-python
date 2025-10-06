#!/bin/bash

# Script to convert deploy-config.env to gcloud run deploy format
# Usage: ./scripts/build-env-vars.sh

set -e

CONFIG_FILE="deploy-config.env"
OUTPUT_FILE="deploy-env-vars.txt"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: $CONFIG_FILE not found"
    exit 1
fi

echo "🔧 Building environment variables from $CONFIG_FILE..."

# Read the config file and convert to gcloud format
ENV_VARS=""
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    if [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    
    # Skip empty values
    if [[ -z "$value" ]]; then
        continue
    fi
    
    # Add to environment variables string
    if [[ -z "$ENV_VARS" ]]; then
        ENV_VARS="$key=$value"
    else
        ENV_VARS="$ENV_VARS,$key=$value"
    fi
done < "$CONFIG_FILE"

# Write to output file
echo "$ENV_VARS" > "$OUTPUT_FILE"

echo "✅ Environment variables built successfully!"
echo "📄 Output written to: $OUTPUT_FILE"
echo ""
echo "📋 Generated environment variables:"
echo "$ENV_VARS"
echo ""
echo "💡 To use in gcloud run deploy:"
echo "   --set-env-vars=\"$(cat $OUTPUT_FILE)\""
