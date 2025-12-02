#!/bin/bash

# Complete Setup Script for Betania Content Automation
# This script walks you through the entire setup process

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║     🚀 Betania Content Automation - Complete Setup         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/home/milanknezevic/Desktop/applications"
cd "$PROJECT_DIR"

# Step 1: Check Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Checking Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"
echo ""

# Step 2: Create virtual environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Setting up Python virtual environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 3: Install dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Installing Python dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will install:"
echo "  - OpenAI SDK"
echo "  - Azure Functions"
echo "  - RSS parsers"
echo "  - Email service (SendGrid)"
echo "  - Database connectors"
echo "  - And more..."
echo ""

cd content_automation
pip install --upgrade pip > /dev/null 2>&1
echo "Installing packages (this may take 1-2 minutes)..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

cd ..
echo ""

# Step 4: Configure credentials
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Configure API credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -f "content_automation/.env" ]; then
    echo "Creating .env file from template..."
    cp content_automation/.env.example content_automation/.env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "You need to configure 3 services:"
echo ""
echo "1️⃣  OpenAI API Key"
echo "   - Go to: https://platform.openai.com/api-keys"
echo "   - Create key, copy it"
echo ""
echo "2️⃣  WordPress Database"
echo "   - Get from your hosting provider (cPanel)"
echo "   - Or from wp-config.php"
echo ""
echo "3️⃣  SendGrid (optional for now)"
echo "   - Sign up: https://signup.sendgrid.com"
echo "   - Create API key"
echo ""

read -p "Do you want to configure credentials now? (y/n): " configure_now

if [[ $configure_now == "y" || $configure_now == "Y" ]]; then
    echo ""
    ./fill_env_simple.sh
else
    echo ""
    echo "⚠️  Credentials not configured. You can configure later by running:"
    echo "   ./fill_env_simple.sh"
    echo ""
    echo "Or manually edit:"
    echo "   nano content_automation/.env"
    echo ""
fi

# Step 5: Test setup (if credentials configured)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Test setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if .env has been configured
if grep -q "your_api_key_here" content_automation/.env 2>/dev/null; then
    echo "⚠️  Credentials not yet configured in .env file"
    echo ""
    echo "Skip testing for now. Configure credentials and run:"
    echo "   source venv/bin/activate"
    echo "   cd content_automation"
    echo "   python test_setup.py"
else
    echo "Running tests..."
    cd content_automation
    python test_setup.py || true
    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 What was installed:"
echo "   ✓ Python virtual environment (venv/)"
echo "   ✓ All Python dependencies"
echo "   ✓ .env configuration file"
echo ""
echo "🎯 Next steps:"
echo ""
echo "1️⃣  If you haven't configured credentials yet:"
echo "   ./fill_env_simple.sh"
echo ""
echo "2️⃣  Test your setup:"
echo "   source venv/bin/activate"
echo "   cd content_automation"
echo "   python test_setup.py"
echo ""
echo "3️⃣  Get credentials you need:"
echo ""
echo "   OpenAI API Key:"
echo "   → https://platform.openai.com/api-keys"
echo ""
echo "   WordPress Database:"
echo "   → From your hosting cPanel or wp-config.php"
echo ""
echo "   SendGrid (optional):"
echo "   → https://signup.sendgrid.com"
echo ""
echo "4️⃣  Read the documentation:"
echo "   - CREDENTIALS_GUIDE.md - How to get each credential"
echo "   - README_SETUP.md - Complete setup guide"
echo "   - QUICK_REFERENCE.md - Common commands"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
