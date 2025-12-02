#!/bin/bash

# Credential Setup Helper Script
# This script helps you gather and set up all required credentials

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🔐 Credential Setup Helper                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f "content_automation/.env" ]; then
    echo "Creating .env file from template..."
    cp content_automation/.env.example content_automation/.env
    echo "✅ .env file created"
fi

echo ""
echo "📋 You need to gather these credentials:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. OpenAI
echo "1️⃣  OPENAI API KEY"
echo "   Where: https://platform.openai.com/api-keys"
echo "   Click: 'Create new secret key'"
echo "   Copy: The key (starts with 'sk-')"
echo ""
read -p "   Enter your OpenAI API key (or press Enter to skip): " openai_key
if [ ! -z "$openai_key" ]; then
    sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" content_automation/.env
    echo "   ✅ OpenAI key saved"
fi
echo ""

# 2. WordPress Admin
echo "2️⃣  WORDPRESS CREDENTIALS"
echo "   URL: Already set to https://betania.io"
echo ""
read -p "   Enter WordPress admin username: " wp_user
if [ ! -z "$wp_user" ]; then
    sed -i "s|WORDPRESS_USERNAME=.*|WORDPRESS_USERNAME=$wp_user|" content_automation/.env
fi

echo ""
echo "   ⚠️  For password, use APPLICATION PASSWORD (not your login password!)"
echo "   Where: https://betania.io/wp-admin/profile.php"
echo "   Scroll to: 'Application Passwords'"
echo "   Name: 'Content Automation'"
echo "   Click: 'Add New Application Password'"
echo "   Copy: The generated password (with spaces)"
echo ""
read -p "   Enter WordPress application password: " wp_pass
if [ ! -z "$wp_pass" ]; then
    sed -i "s|WORDPRESS_PASSWORD=.*|WORDPRESS_PASSWORD=$wp_pass|" content_automation/.env
    echo "   ✅ WordPress credentials saved"
fi
echo ""

# 3. WordPress Database
echo "3️⃣  WORDPRESS DATABASE CREDENTIALS"
echo "   Where: Your hosting provider (cPanel, Plesk, etc.)"
echo "   Or check: wp-config.php file"
echo ""
read -p "   Database host (usually 'localhost'): " db_host
db_host=${db_host:-localhost}
sed -i "s|WORDPRESS_DB_HOST=.*|WORDPRESS_DB_HOST=$db_host|" content_automation/.env

read -p "   Database name: " db_name
if [ ! -z "$db_name" ]; then
    sed -i "s|WORDPRESS_DB_NAME=.*|WORDPRESS_DB_NAME=$db_name|" content_automation/.env
fi

read -p "   Database user: " db_user
if [ ! -z "$db_user" ]; then
    sed -i "s|WORDPRESS_DB_USER=.*|WORDPRESS_DB_USER=$db_user|" content_automation/.env
fi

read -p "   Database password: " db_pass
if [ ! -z "$db_pass" ]; then
    sed -i "s|WORDPRESS_DB_PASSWORD=.*|WORDPRESS_DB_PASSWORD=$db_pass|" content_automation/.env
    echo "   ✅ Database credentials saved"
fi
echo ""

# 4. SendGrid
echo "4️⃣  SENDGRID API KEY"
echo "   Where: https://sendgrid.com (free account)"
echo "   Steps:"
echo "     1. Sign up at https://signup.sendgrid.com"
echo "     2. Settings → API Keys → Create API Key"
echo "     3. Name: 'Betania Newsletter'"
echo "     4. Permissions: Full Access (or Mail Send)"
echo "     5. Copy the key (starts with 'SG.')"
echo ""
echo "   ⚠️  IMPORTANT: Verify sender email at SendGrid!"
echo "   Settings → Sender Authentication → Verify Single Sender"
echo "   Use: newsletter@betania.io"
echo ""
read -p "   Enter SendGrid API key (or press Enter to skip): " sendgrid_key
if [ ! -z "$sendgrid_key" ]; then
    sed -i "s|SENDGRID_API_KEY=.*|SENDGRID_API_KEY=$sendgrid_key|" content_automation/.env
    echo "   ✅ SendGrid key saved"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Local credentials configured in: content_automation/.env"
echo ""
echo "📝 Next steps:"
echo "   1. Test your setup: python content_automation/test_setup.py"
echo "   2. Set up Azure credentials for CI/CD (see below)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔐 AZURE CREDENTIALS FOR CI/CD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For automated deployment (GitHub Actions), you need Azure Service Principal:"
echo ""
echo "Run this command:"
echo "  az login  # Login to Azure first"
echo "  az ad sp create-for-rbac --name \"betania-automation\" \\"
echo "    --role contributor \\"
echo "    --scopes /subscriptions/\$(az account show --query id -o tsv) \\"
echo "    --sdk-auth"
echo ""
echo "This will output JSON credentials. Save them for GitHub Secrets!"
echo ""
echo "Then add secrets to GitHub:"
echo "  Repository → Settings → Secrets → Actions → New secret"
echo ""
echo "See DEPLOYMENT_QUICKSTART.md for full guide"
echo ""
