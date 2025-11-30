# Quick Reference Guide

## 🚀 Getting Started (First Time)

```bash
# 1. Setup environment
cd content_automation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
nano .env  # Fill in your credentials

# 3. Test setup
python test_setup.py

# 4. Initialize database
python -c "from models.database import Database; db = Database(); db.init_tables()"
```

## 🔑 Getting Required Credentials

### OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy and save the key
4. Add to `.env`: `OPENAI_API_KEY=sk-...`

### WordPress Application Password
1. Login to WordPress admin: `https://betania.io/wp-admin`
2. Go to: Users → Your Profile
3. Scroll to "Application Passwords"
4. Name: "Content Automation"
5. Click "Add New Application Password"
6. Copy the password (remove spaces)
7. Add to `.env`:
   ```
   WORDPRESS_USERNAME=your_username
   WORDPRESS_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### WordPress Database Credentials
Ask your hosting provider or check:
- cPanel → MySQL Databases
- Or check `wp-config.php` file

Add to `.env`:
```
WORDPRESS_DB_HOST=localhost
WORDPRESS_DB_NAME=your_database
WORDPRESS_DB_USER=your_user
WORDPRESS_DB_PASSWORD=your_password
```

### SendGrid API Key
1. Sign up: https://sendgrid.com (free tier: 100 emails/day)
2. Go to: Settings → API Keys
3. Create API Key with "Mail Send" permissions
4. Copy the key
5. **Verify sender email**: Settings → Sender Authentication
6. Add to `.env`:
   ```
   SENDGRID_API_KEY=SG.xxx...
   SENDGRID_FROM_EMAIL=newsletter@betania.io
   ```

## 📝 Common Commands

### Testing Individual Components

```bash
# Test WordPress connection
python services/wordpress_client.py

# Test RSS fetching
python services/rss_aggregator.py

# Test AI generation
python services/ai_content_generator.py

# Test email service
python services/email_service.py

# Test database
python models/database.py
```

### Manual Runs

```bash
# Run daily content generation once
python functions/daily_content/__init__.py

# Run weekly newsletter once
python functions/weekly_newsletter/__init__.py

# Run full system test
python test_setup.py
```

### Database Operations

```bash
# Initialize tables
python -c "from models.database import Database; db = Database(); db.init_tables()"

# Check subscribers
python -c "
from models.database import Database, SubscriberModel
db = Database()
sm = SubscriberModel(db)
subs = sm.get_active_subscribers()
print(f'Active subscribers: {len(subs)}')
for s in subs[:5]:
    print(f'  - {s[\"email\"]} ({s[\"name\"]})')
"

# Add test subscriber
python -c "
from models.database import Database, SubscriberModel
db = Database()
sm = SubscriberModel(db)
sm.add_subscriber('test@example.com', 'Test User')
"
```

## 🌐 Local Testing with Azure Functions

```bash
# Install Azure Functions Core Tools
# Ubuntu/Debian:
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install azure-functions-core-tools-4

# Start local Azure Functions
cd content_automation
func start

# Trigger functions manually
# Visit: http://localhost:7071/admin/functions/{function-name}
```

## ☁️ Azure Deployment

```bash
# Login
az login

# Create resources (first time only)
az group create --name betania-automation --location eastus
az storage account create --name betaniastorage --resource-group betania-automation --sku Standard_LRS
az functionapp create \
  --resource-group betania-automation \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name betania-content-automation \
  --storage-account betaniastorage \
  --os-type Linux

# Set environment variables in Azure
az functionapp config appsettings set \
  --name betania-content-automation \
  --resource-group betania-automation \
  --settings @azure-settings.json

# Deploy
func azure functionapp publish betania-content-automation

# View logs
az functionapp log tail --name betania-content-automation --resource-group betania-automation
```

## 📊 Monitoring

### Check Logs

```bash
# Local logs
tail -f /var/log/azure-functions.log

# Azure logs
az functionapp log tail --name betania-content-automation --resource-group betania-automation
```

### Database Queries

```sql
-- Check recent articles
SELECT title, source_name, published_at, wordpress_url
FROM published_articles
ORDER BY published_at DESC
LIMIT 10;

-- Check active subscribers
SELECT COUNT(*) as total,
       SUM(confirmed) as confirmed,
       SUM(active) as active
FROM newsletter_subscribers;

-- Check LinkedIn queue
SELECT COUNT(*) as pending
FROM linkedin_queue
WHERE posted = FALSE;

-- Newsletter sends
SELECT sent_at, subject, recipient_count
FROM newsletter_sends
ORDER BY sent_at DESC
LIMIT 5;
```

## 🐛 Troubleshooting Quick Fixes

### Import Errors
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### WordPress 401 Unauthorized
```bash
# Test authentication
curl -u "username:app_password" https://betania.io/wp-json/wp/v2/posts?per_page=1
```

### Database Connection Failed
```bash
# Test MySQL connection
mysql -h your_host -u your_user -p

# Check if tables exist
mysql -h your_host -u your_user -p -e "SHOW TABLES" your_database
```

### OpenAI Rate Limit
Edit `.env`:
```
MAX_ARTICLES_PER_DAY=2  # Reduce from 5
```

### SendGrid Emails Not Sending
```bash
# Verify sender
# Go to: https://app.sendgrid.com/settings/sender_auth
# Make sure newsletter@betania.io is verified
```

## 🔄 Updating RSS Feeds

Edit [config.py](config.py):

```python
RSS_FEEDS = [
    "https://devblogs.microsoft.com/dotnet/feed/",
    "https://your-new-feed.com/rss",  # Add here
    # ...
]
```

## ⏰ Changing Schedule

Edit `function.json` files:

**Daily at 6 AM instead of 9 AM:**
```json
{
  "schedule": "0 0 6 * * *"
}
```

**Twice daily (9 AM and 6 PM):**
```json
{
  "schedule": "0 0 9,18 * * *"
}
```

**Newsletter on Friday instead of Sunday:**
```json
{
  "schedule": "0 0 10 * * FRI"
}
```

## 📦 Installing WordPress Plugin

```bash
# Method 1: Via WordPress admin
cd wordpress
zip betania-newsletter.zip newsletter-subscription.php
# Upload via WordPress → Plugins → Add New → Upload

# Method 2: Via FTP
scp wordpress/newsletter-subscription.php user@betania.io:/path/to/wp-content/plugins/

# Method 3: Via SSH
ssh user@betania.io
cd /path/to/wp-content/plugins/
nano newsletter-subscription.php  # Paste content
```

Then activate in WordPress admin: Plugins → Activate

Add to any page: `[betania_newsletter_form]`

## 📧 Subscriber Management

### Export Subscribers
```bash
python -c "
from models.database import Database, SubscriberModel
import csv
db = Database()
sm = SubscriberModel(db)
subs = sm.get_active_subscribers()
with open('subscribers.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['email', 'name', 'subscribed_at'])
    writer.writeheader()
    writer.writerows(subs)
print('Exported to subscribers.csv')
"
```

### Manually Add Subscribers
```bash
python -c "
from models.database import Database, SubscriberModel
db = Database()
sm = SubscriberModel(db)
sm.add_subscriber('email@example.com', 'Full Name')
sm.confirm_subscriber('token')  # Auto-confirm
"
```

## 🎯 Next Steps Checklist

- [ ] Fill in all `.env` credentials
- [ ] Run `python test_setup.py` (all tests should pass)
- [ ] Install WordPress plugin
- [ ] Test manual run: `python functions/daily_content/__init__.py`
- [ ] Deploy to Azure
- [ ] Monitor for 1 week
- [ ] Review and adjust RSS feeds
- [ ] Build LinkedIn queue dashboard (future)

## 📚 Documentation Files

- [README_SETUP.md](README_SETUP.md) - Complete setup guide
- [WORDPRESS_PLUGIN_INSTRUCTIONS.md](WORDPRESS_PLUGIN_INSTRUCTIONS.md) - Plugin details
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - This file
- [README.md](../README.md) - Project overview

## 💡 Pro Tips

1. **Start with Draft Mode**: Change `status='draft'` in daily_content function to review posts before publishing
2. **Test with Few Feeds**: Start with 3-5 RSS feeds, add more later
3. **Monitor Costs**: Check OpenAI usage dashboard monthly
4. **Backup Database**: Regular backups of `newsletter_subscribers` table
5. **Version Control**: Commit `.env.example` but never `.env`

## 🆘 Getting Help

1. Check logs first
2. Run `python test_setup.py` to identify failing component
3. Review relevant documentation file
4. Check Azure Portal for Function errors
5. Review database for data issues

---

**Last Updated**: 2025-11-30
