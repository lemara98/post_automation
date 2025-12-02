#!/bin/bash

ENV_FILE="content_automation/.env"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🔐 Fill .env File Interactively                    ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Azure OpenAI Configuration
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  AZURE OPENAI CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Where to get these:"
echo "  1. Go to: https://portal.azure.com"
echo "  2. Search: 'Azure OpenAI'"
echo "  3. Create or select your OpenAI resource"
echo "  4. Keys and Endpoint → Copy values"
echo ""

read -p "Azure OpenAI API Key: " azure_openai_key
read -p "Azure OpenAI Endpoint (e.g., https://your-resource.openai.azure.com/): " azure_openai_endpoint
read -p "Deployment Name (default: gpt-4): " azure_deployment
azure_deployment=${azure_deployment:-gpt-4}
read -p "API Version (default: 2024-02-15-preview): " azure_api_version
azure_api_version=${azure_api_version:-2024-02-15-preview}

if [ ! -z "$azure_openai_key" ]; then
    sed -i "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$azure_openai_key|" $ENV_FILE
    sed -i "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$azure_openai_endpoint|" $ENV_FILE
    sed -i "s|AZURE_OPENAI_DEPLOYMENT_NAME=.*|AZURE_OPENAI_DEPLOYMENT_NAME=$azure_deployment|" $ENV_FILE
    sed -i "s|AZURE_OPENAI_API_VERSION=.*|AZURE_OPENAI_API_VERSION=$azure_api_version|" $ENV_FILE
    echo "✅ Azure OpenAI configuration saved"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  WORDPRESS DATABASE CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Where to get these:"
echo "  - From your hosting provider (cPanel → MySQL Databases)"
echo "  - Or from your wp-config.php file on the server"
echo ""

read -p "Database Host (default: localhost): " db_host
db_host=${db_host:-localhost}
read -p "Database Name: " db_name
read -p "Database User: " db_user
read -sp "Database Password: " db_password
echo ""

if [ ! -z "$db_name" ]; then
    sed -i "s|WORDPRESS_DB_HOST=.*|WORDPRESS_DB_HOST=$db_host|" $ENV_FILE
    sed -i "s|WORDPRESS_DB_NAME=.*|WORDPRESS_DB_NAME=$db_name|" $ENV_FILE
    sed -i "s|WORDPRESS_DB_USER=.*|WORDPRESS_DB_USER=$db_user|" $ENV_FILE
    sed -i "s|WORDPRESS_DB_PASSWORD=.*|WORDPRESS_DB_PASSWORD=$db_password|" $ENV_FILE
    echo "✅ Database configuration saved"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  SENDGRID CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Where to get this:"
echo "  1. Sign up: https://signup.sendgrid.com (FREE)"
echo "  2. Settings → API Keys → Create API Key"
echo "  3. Name: 'Betania Newsletter'"
echo "  4. Permissions: Full Access"
echo "  5. Copy the key (starts with SG.)"
echo ""
echo "⚠️  IMPORTANT: After getting key, verify sender email:"
echo "   Settings → Sender Authentication → Verify Single Sender"
echo "   Email: newsletter@betania.io"
echo ""

read -p "SendGrid API Key: " sendgrid_key
read -p "From Email (default: newsletter@betania.io): " from_email
from_email=${from_email:-newsletter@betania.io}
read -p "From Name (default: Betania Tech Newsletter): " from_name
from_name=${from_name:-Betania Tech Newsletter}

if [ ! -z "$sendgrid_key" ]; then
    sed -i "s|SENDGRID_API_KEY=.*|SENDGRID_API_KEY=$sendgrid_key|" $ENV_FILE
    sed -i "s|SENDGRID_FROM_EMAIL=.*|SENDGRID_FROM_EMAIL=$from_email|" $ENV_FILE
    sed -i "s|SENDGRID_FROM_NAME=.*|SENDGRID_FROM_NAME=$from_name|" $ENV_FILE
    echo "✅ SendGrid configuration saved"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Configuration saved to: $ENV_FILE"
echo ""
echo "🧪 Test your configuration:"
echo "   cd content_automation"
echo "   python test_setup.py"
echo ""
echo "📋 View configuration (without showing secrets):"
echo "   grep -E '^[A-Z_]+=.+' $ENV_FILE | grep -v PASSWORD | grep -v API_KEY"
echo ""
