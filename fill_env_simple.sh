#!/bin/bash

ENV_FILE="content_automation/.env"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🔐 Fill .env File - Simple Version                 ║"
echo "║          (Using regular OpenAI, not Azure OpenAI)           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Regular OpenAI (simpler!)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  OPENAI API KEY (Regular OpenAI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Where to get this:"
echo "  1. Go to: https://platform.openai.com/api-keys"
echo "  2. Sign up or login"
echo "  3. Click: 'Create new secret key'"
echo "  4. Name it: 'Betania Content Automation'"
echo "  5. Copy the key (starts with 'sk-proj-' or 'sk-')"
echo ""
echo "Cost: ~\$22/month for 5 articles per day"
echo ""

read -p "OpenAI API Key: " openai_key

if [ ! -z "$openai_key" ]; then
    sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" $ENV_FILE
    # Comment out Azure OpenAI settings since we're using regular OpenAI
    sed -i "s|^AZURE_OPENAI_API_KEY=|# AZURE_OPENAI_API_KEY=|" $ENV_FILE
    sed -i "s|^AZURE_OPENAI_ENDPOINT=|# AZURE_OPENAI_ENDPOINT=|" $ENV_FILE
    sed -i "s|^AZURE_OPENAI_DEPLOYMENT_NAME=|# AZURE_OPENAI_DEPLOYMENT_NAME=|" $ENV_FILE
    sed -i "s|^AZURE_OPENAI_API_VERSION=|# AZURE_OPENAI_API_VERSION=|" $ENV_FILE
    echo "✅ OpenAI API key saved"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  WORDPRESS DATABASE CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Where to get these:"
echo "  Option A: From your hosting provider"
echo "    - cPanel → MySQL Databases"
echo "    - Look for existing WordPress database"
echo ""
echo "  Option B: From wp-config.php on your server"
echo "    - SSH into betania.io"
echo "    - Look for DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
echo ""

read -p "Database Host (default: localhost): " db_host
db_host=${db_host:-localhost}
read -p "Database Name (e.g., betania_wp): " db_name
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
echo "  1. Sign up: https://signup.sendgrid.com (FREE!)"
echo "  2. Complete email verification"
echo "  3. Settings → API Keys → Create API Key"
echo "  4. Name: 'Betania Newsletter'"
echo "  5. Permissions: 'Full Access' or 'Mail Send'"
echo "  6. Copy the key (starts with 'SG.')"
echo ""
echo "⚠️  IMPORTANT STEP - Verify sender email:"
echo "   1. Go to: Settings → Sender Authentication"
echo "   2. Click: 'Verify a Single Sender'"
echo "   3. Email: newsletter@betania.io"
echo "   4. Complete verification in your inbox"
echo ""
echo "Cost: FREE (up to 100 emails per day = 3,000/month)"
echo ""

read -p "SendGrid API Key (or press Enter to skip): " sendgrid_key
read -p "From Email (default: newsletter@betania.io): " from_email
from_email=${from_email:-newsletter@betania.io}
read -p "From Name (default: Betania Tech Newsletter): " from_name
from_name=${from_name:-Betania Tech Newsletter}

if [ ! -z "$sendgrid_key" ]; then
    sed -i "s|SENDGRID_API_KEY=.*|SENDGRID_API_KEY=$sendgrid_key|" $ENV_FILE
    sed -i "s|SENDGRID_FROM_EMAIL=.*|SENDGRID_FROM_EMAIL=$from_email|" $ENV_FILE
    sed -i "s|SENDGRID_FROM_NAME=.*|SENDGRID_FROM_NAME=$from_name|" $ENV_FILE
    echo "✅ SendGrid configuration saved"
else
    echo "⚠️  SendGrid skipped - newsletter feature won't work until configured"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Configuration saved to: $ENV_FILE"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Test your configuration:"
echo "   cd content_automation"
echo "   python test_setup.py"
echo ""
echo "2️⃣  If using SendGrid, verify sender email:"
echo "   https://app.sendgrid.com/settings/sender_auth"
echo ""
echo "3️⃣  View your config (secrets hidden):"
echo "   grep -E '^[A-Z_]+=.+' $ENV_FILE | grep -v PASSWORD | grep -v API_KEY | grep -v SECRET"
echo ""
echo "4️⃣  Missing credentials? Re-run this script or edit .env manually:"
echo "   nano $ENV_FILE"
echo ""
