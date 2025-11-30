# Betania Content Automation System

## 📋 Overview

Automated content pipeline that:
- ✅ Fetches articles from RSS feeds daily
- ✅ Generates blog posts using AI (GPT-4)
- ✅ Auto-publishes to WordPress (betania.io)
- ✅ Queues LinkedIn posts for manual review
- ✅ Sends weekly newsletter to subscribers with Top 5 articles

## 🏗️ Architecture

```
Daily (9:00 AM):
RSS Feeds → AI Generation → WordPress → Database → LinkedIn Queue

Weekly (Sunday 10:00 AM):
Database → AI Ranking (Top 5) → Email → Subscribers
```

## 📦 Prerequisites

### Required Accounts & Services

1. **OpenAI or Azure OpenAI**
   - OpenAI API key OR Azure OpenAI deployment
   - GPT-4 access recommended

2. **WordPress (betania.io)**
   - Admin access
   - Application Password (Settings → Users → Your Profile → Application Passwords)
   - Or JWT authentication

3. **SendGrid**
   - Free account: https://sendgrid.com/
   - API key with Mail Send permissions
   - Verified sender email

4. **WordPress Database Access**
   - MySQL/MariaDB credentials
   - Usually provided by your hosting provider

5. **Azure Account** (for deployment)
   - Free tier is sufficient for testing
   - Azure Functions for hosting

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd content_automation
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and fill in your credentials
nano .env  # or use your favorite editor
```

### 3. Set Up WordPress

#### Option A: Install Plugin (Recommended)

1. Copy `wordpress/newsletter-subscription.php` to your WordPress plugins directory:
   ```bash
   # Via FTP or SSH
   scp wordpress/newsletter-subscription.php user@betania.io:/path/to/wordpress/wp-content/plugins/
   ```

2. Activate the plugin in WordPress admin:
   - Go to Plugins → Installed Plugins
   - Find "Betania Newsletter Subscription"
   - Click "Activate"

3. Add subscription form to a page:
   - Create a new page: "Newsletter"
   - Add this shortcode: `[betania_newsletter_form]`
   - Publish!

#### Option B: Manual Database Setup

If you can't install the plugin, run this SQL in your WordPress database:

```sql
CREATE TABLE IF NOT EXISTS wp_newsletter_subscribers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirmed BOOLEAN DEFAULT FALSE,
    confirmation_token VARCHAR(64),
    unsubscribe_token VARCHAR(64) UNIQUE,
    active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add other tables
-- (See models/database.py for complete schema)
```

### 4. Initialize Database

```bash
cd content_automation
python -c "from models.database import Database; db = Database(); db.init_tables()"
```

### 5. Test Individual Components

#### Test WordPress Connection

```bash
python services/wordpress_client.py
```

Expected output: ✓ WordPress connection successful!

#### Test RSS Fetching

```bash
python services/rss_aggregator.py
```

Expected output: List of recent articles

#### Test AI Generation

```bash
python services/ai_content_generator.py
```

Expected output: Generated blog post and LinkedIn post

#### Test Email Service

```bash
python services/email_service.py
```

Expected output: Test emails sent

### 6. Test Azure Functions Locally

```bash
# Install Azure Functions Core Tools
# Ubuntu/Debian:
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4

# Run locally
cd content_automation
func start
```

### 7. Manual Test Run

Run daily content generation manually:

```bash
python functions/daily_content/__init__.py
```

Run weekly newsletter manually:

```bash
python functions/weekly_newsletter/__init__.py
```

## 🔐 Environment Variables

### Required Variables

```bash
# OpenAI (choose one)
OPENAI_API_KEY=sk-...                           # Direct OpenAI
# OR
AZURE_OPENAI_API_KEY=...                        # Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# WordPress
WORDPRESS_URL=https://betania.io
WORDPRESS_USERNAME=your_admin_username
WORDPRESS_PASSWORD=your_application_password    # NOT your login password!

# WordPress Database
WORDPRESS_DB_HOST=localhost                     # Or your host's DB server
WORDPRESS_DB_NAME=wordpress_db
WORDPRESS_DB_USER=db_user
WORDPRESS_DB_PASSWORD=db_password

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=newsletter@betania.io      # Must be verified in SendGrid
SENDGRID_FROM_NAME=Betania Tech Newsletter
```

### Optional Variables

```bash
ENVIRONMENT=production
MAX_ARTICLES_PER_DAY=5                          # How many blog posts per day
MAX_NEWSLETTER_ARTICLES=5                       # How many in weekly newsletter
```

## 📅 Automation Schedule

### Daily Content Generation
- **Time**: 9:00 AM (every day)
- **Cron**: `0 0 9 * * *`
- **Actions**:
  1. Fetch articles from RSS feeds (past 24 hours)
  2. Filter out already published articles
  3. Process up to 5 articles
  4. Generate blog post with AI
  5. Publish to WordPress
  6. Queue LinkedIn post

### Weekly Newsletter
- **Time**: 10:00 AM (every Sunday)
- **Cron**: `0 0 10 * * SUN`
- **Actions**:
  1. Fetch all articles from past 7 days
  2. Use AI to select top 5 articles
  3. Generate newsletter intro
  4. Send to all active subscribers

## 🌐 Deployment to Azure

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name betania-content-automation --location eastus

# Create storage account
az storage account create \
  --name betaniastorage \
  --resource-group betania-content-automation \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --resource-group betania-content-automation \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name betania-content-automation \
  --storage-account betaniastorage \
  --os-type Linux
```

### 2. Configure Application Settings

```bash
# Set environment variables in Azure
az functionapp config appsettings set \
  --name betania-content-automation \
  --resource-group betania-content-automation \
  --settings \
  OPENAI_API_KEY=your_key \
  WORDPRESS_URL=https://betania.io \
  WORDPRESS_USERNAME=your_username \
  WORDPRESS_PASSWORD=your_app_password \
  WORDPRESS_DB_HOST=your_db_host \
  WORDPRESS_DB_NAME=your_db_name \
  WORDPRESS_DB_USER=your_db_user \
  WORDPRESS_DB_PASSWORD=your_db_password \
  SENDGRID_API_KEY=your_sendgrid_key \
  SENDGRID_FROM_EMAIL=newsletter@betania.io \
  SENDGRID_FROM_NAME="Betania Tech Newsletter"
```

### 3. Deploy

```bash
cd content_automation
func azure functionapp publish betania-content-automation
```

### 4. Verify Deployment

```bash
# Check function logs
az functionapp log tail --name betania-content-automation --resource-group betania-content-automation

# Test function
az functionapp function show \
  --name betania-content-automation \
  --resource-group betania-content-automation \
  --function-name daily_content
```

## 📊 Monitoring & Logs

### View Logs in Azure Portal

1. Go to Azure Portal → Function App
2. Click "Log stream" in left menu
3. Watch real-time logs

### Check Database

```bash
# Connect to your WordPress database
mysql -h your_host -u your_user -p

USE your_database;

# Check subscribers
SELECT * FROM newsletter_subscribers WHERE active = 1;

# Check published articles
SELECT * FROM published_articles ORDER BY published_at DESC LIMIT 10;

# Check LinkedIn queue
SELECT * FROM linkedin_queue WHERE posted = 0;
```

## 🔧 Customization

### Add More RSS Feeds

Edit `config.py` and add URLs to `RSS_FEEDS` list:

```python
RSS_FEEDS = [
    "https://devblogs.microsoft.com/dotnet/feed/",
    "https://your-new-feed.com/rss",
    # ... more feeds
]
```

### Change Schedule

Edit `function.json` files:

```json
{
  "schedule": "0 0 9 * * *"  // Cron expression
}
```

Cron format: `second minute hour day month weekday`

Examples:
- Every day at 6 AM: `0 0 6 * * *`
- Every Monday at 9 AM: `0 0 9 * * MON`
- Twice daily (9 AM, 6 PM): `0 0 9,18 * * *`

### Change Post Status

In `functions/daily_content/__init__.py`, change:

```python
wp_post = wp_client.create_post(
    status='draft',  # Change to 'draft' for manual review
    # ...
)
```

## 🐛 Troubleshooting

### WordPress Connection Fails

**Error**: 401 Unauthorized

**Solution**:
1. Go to WordPress → Users → Your Profile
2. Scroll to "Application Passwords"
3. Create new password named "Content Automation"
4. Copy the generated password (with spaces removed)
5. Update `.env` with this password

### Database Connection Fails

**Error**: Can't connect to MySQL server

**Solution**:
1. Check database credentials
2. Ensure database allows remote connections
3. Check firewall rules
4. Try connecting with mysql command:
   ```bash
   mysql -h your_host -u your_user -p
   ```

### SendGrid Emails Not Sending

**Error**: 403 Forbidden

**Solution**:
1. Verify your sender email in SendGrid:
   - Settings → Sender Authentication
   - Verify a Single Sender
2. Check API key permissions (needs Mail Send)
3. Check daily send limit (free tier: 100/day)

### OpenAI Rate Limit

**Error**: Rate limit exceeded

**Solution**:
1. Reduce `MAX_ARTICLES_PER_DAY` in `.env`
2. Add delays between API calls
3. Upgrade OpenAI plan

## 📈 Cost Estimates

### Free Tier (for testing)
- Azure Functions: Free (1M executions/month)
- SendGrid: Free (100 emails/day)
- OpenAI: ~$5-10/month (depends on usage)
- **Total**: ~$5-10/month

### Production (1000 subscribers)
- Azure Functions: ~$10/month
- SendGrid: Free tier sufficient
- OpenAI: ~$20-30/month
- **Total**: ~$30-40/month

## 🔒 Security Best Practices

1. **Never commit `.env` file** - it's in `.gitignore`
2. **Use Application Passwords** for WordPress (not your admin password)
3. **Rotate API keys** regularly
4. **Enable double opt-in** for subscribers (already implemented)
5. **Use Azure Key Vault** for production secrets

## 📧 Support

### Issues & Questions

Create an issue on GitHub or contact: your-email@betania.io

### Logs Location

- Local: `console output`
- Azure: Portal → Function App → Log Stream

## 🎉 What's Next?

1. ✅ Test the system locally
2. ✅ Deploy to Azure
3. ✅ Monitor for a week
4. 🔜 Add analytics/tracking
5. 🔜 Build LinkedIn queue dashboard
6. 🔜 Add A/B testing for subject lines
7. 🔜 Implement article recommendations

---

**Built with ❤️ using Python, Azure Functions, WordPress, and GPT-4**
