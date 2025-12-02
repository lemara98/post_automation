# Complete Credentials Guide

This guide shows ALL credentials needed for the Betania Content Automation system.

---

## 📋 Overview

You need **TWO SETS** of credentials:

1. **Local Development** (`.env` file) - For running locally
2. **Azure Credentials** (for CI/CD) - For automated deployment

---

## 🔑 Part 1: Local Development Credentials

These go in `content_automation/.env` file.

### Quick Setup

Run this interactive script:
```bash
./setup_credentials.sh
```

Or manually edit `content_automation/.env` with the credentials below:

---

### 1. OpenAI API Key

**What:** AI service for content generation (main cost: ~$22/month)

**Where to get:**
1. Go to: https://platform.openai.com/api-keys
2. Sign up/login
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

**In .env:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Cost:** ~$22/month (see [COST_BREAKDOWN.md](COST_BREAKDOWN.md))

**Test:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

### 2. WordPress Admin Credentials

**What:** To publish blog posts automatically

**Where to get:**

**Username:** Your WordPress admin username (you already have this)

**Application Password** (NOT your login password!):
1. Go to: https://betania.io/wp-admin/profile.php
2. Scroll to "Application Passwords" section
3. Application Name: `Content Automation`
4. Click "Add New Application Password"
5. Copy the generated password (it has spaces - keep them!)

**In .env:**
```bash
WORDPRESS_URL=https://betania.io
WORDPRESS_USERNAME=your_admin_username
WORDPRESS_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**Important:**
- ✅ Use Application Password (generated above)
- ❌ DON'T use your WordPress login password
- ✅ Keep the spaces in the password

**Test:**
```bash
cd content_automation
python -c "from services.wordpress_client import WordPressClient; wp = WordPressClient(); wp.test_connection()"
```

---

### 3. WordPress Database Credentials

**What:** To store newsletter subscribers

**Where to get:**

**Option A: From your hosting provider**
- cPanel → MySQL Databases
- Plesk → Databases
- Or ask your hosting support

**Option B: From wp-config.php**
```bash
# SSH into your server
ssh user@betania.io

# View database config
grep DB_ wp-config.php
```

You'll see:
```php
define('DB_NAME', 'wordpress_db');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'password');
define('DB_HOST', 'localhost');
```

**In .env:**
```bash
WORDPRESS_DB_HOST=localhost  # or your host's DB server
WORDPRESS_DB_NAME=wordpress_db
WORDPRESS_DB_USER=wp_user
WORDPRESS_DB_PASSWORD=your_db_password
```

**Test:**
```bash
cd content_automation
python -c "from models.database import Database; db = Database(); db.test_connection()"
```

---

### 4. SendGrid API Key

**What:** Email service for newsletters (FREE for up to 100 emails/day)

**Where to get:**
1. Sign up: https://signup.sendgrid.com (FREE account)
2. Complete email verification
3. Settings → API Keys → Create API Key
4. Name: `Betania Newsletter`
5. Permissions: **Full Access** (or at minimum "Mail Send")
6. Copy the key (starts with `SG.`)

**IMPORTANT: Verify Sender Email!**
1. Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Email: `newsletter@betania.io`
4. Complete verification

**In .env:**
```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=newsletter@betania.io
SENDGRID_FROM_NAME=Betania Tech Newsletter
```

**Test:**
```bash
cd content_automation
python services/email_service.py
# Check your email for test message
```

---

## ☁️ Part 2: Azure Credentials (For CI/CD)

These are ONLY needed if you want automated deployment via GitHub Actions or Azure DevOps.

### Why You Need This

**Local development:** Uses `az login` (your personal Azure account)

**CI/CD (automated):** GitHub Actions can't use `az login`, so it needs a **Service Principal** (like a robot account)

---

### Creating Azure Service Principal

**Step 1: Login to Azure**
```bash
az login
```

**Step 2: Create Service Principal**
```bash
az ad sp create-for-rbac \
  --name "betania-content-automation" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth
```

**Step 3: Save the output!**

You'll get JSON like this:
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-secret-here",
  "subscriptionId": "87654321-4321-4321-4321-210987654321",
  "tenantId": "11111111-1111-1111-1111-111111111111",
  ...
}
```

**⚠️ IMPORTANT: Save this entire JSON!** You'll need it for GitHub Secrets.

---

### Adding Secrets to GitHub

**Go to:** Your GitHub repository → Settings → Secrets and variables → Actions

**Click:** "New repository secret" for EACH of these:

| Secret Name | Value | Where to get |
|------------|-------|--------------|
| `AZURE_CREDENTIALS` | The ENTIRE JSON from Step 2 | Service principal output |
| `OPENAI_API_KEY` | `sk-...` | Same as .env |
| `WORDPRESS_USERNAME` | Your WP username | Same as .env |
| `WORDPRESS_PASSWORD` | Application password | Same as .env |
| `WORDPRESS_DB_HOST` | Database host | Same as .env |
| `WORDPRESS_DB_NAME` | Database name | Same as .env |
| `WORDPRESS_DB_USER` | Database user | Same as .env |
| `WORDPRESS_DB_PASSWORD` | Database password | Same as .env |
| `SENDGRID_API_KEY` | `SG.....` | Same as .env |

**Total: 9 secrets**

---

## ✅ Verification Checklist

### Local Development

- [ ] Created `content_automation/.env` from template
- [ ] Added OpenAI API key
- [ ] Added WordPress username + application password
- [ ] Added WordPress database credentials
- [ ] Added SendGrid API key
- [ ] Verified SendGrid sender email
- [ ] Ran `python content_automation/test_setup.py` - all tests pass

### CI/CD (Optional)

- [ ] Logged into Azure: `az login`
- [ ] Created Service Principal
- [ ] Saved JSON output
- [ ] Added all 9 secrets to GitHub
- [ ] Pushed code to trigger deployment

---

## 🧪 Testing Your Setup

### Test Everything

```bash
cd content_automation
python test_setup.py
```

Expected output:
```
✓ Configuration loaded successfully
✓ Database connection successful
✓ WordPress API connection successful
✓ Fetched X articles
✓ LinkedIn post generated
✓ Email service initialized

Results: 6/6 tests passed
```

### Test Individual Services

```bash
# Test OpenAI
python -c "from services.ai_content_generator import AIContentGenerator; ai = AIContentGenerator(); print('✓ OpenAI working')"

# Test WordPress
python services/wordpress_client.py

# Test Database
python models/database.py

# Test Email
python services/email_service.py
```

---

## 🚨 Troubleshooting

### "No OpenAI API key configured"

**Fix:**
```bash
# Check .env file exists
ls content_automation/.env

# Check key is set
grep OPENAI_API_KEY content_automation/.env

# Make sure no quotes around the key
# ✅ Correct: OPENAI_API_KEY=sk-xxx
# ❌ Wrong:   OPENAI_API_KEY="sk-xxx"
```

### "WordPress connection failed: 401"

**Fix:**
- Make sure you're using **Application Password**, not login password
- Generate new one: https://betania.io/wp-admin/profile.php
- Keep the spaces in the password

### "Database connection failed"

**Fix:**
```bash
# Test MySQL connection manually
mysql -h localhost -u wp_user -p
# If this fails, your credentials are wrong

# Check with hosting provider:
# cPanel → MySQL Databases
```

### "SendGrid 403 Forbidden"

**Fix:**
- Verify sender email in SendGrid dashboard
- Settings → Sender Authentication → Verify Single Sender
- Use `newsletter@betania.io`

---

## 🔐 Security Best Practices

### ✅ DO:
- Use `.env` file for local secrets (already in .gitignore)
- Use GitHub Secrets for CI/CD
- Use WordPress Application Passwords (not admin password)
- Rotate secrets quarterly
- Use minimum required permissions

### ❌ DON'T:
- Commit `.env` file to git (it's already in .gitignore)
- Share API keys in chat/email
- Use your main WordPress password
- Give service principal more than "Contributor" role

---

## 📊 Cost of Credentials

| Service | Credential Type | Cost |
|---------|----------------|------|
| OpenAI | API Key | ~$22/month |
| WordPress | Hosting | Already have |
| WordPress DB | Same as hosting | $0 |
| SendGrid | API Key | FREE (up to 100/day) |
| Azure | Service Principal | $0 (just identity) |
| GitHub | SSH Key | FREE |

**Total additional cost: ~$22/month** (just OpenAI)

---

## 🎯 Quick Reference

**Local setup:**
```bash
./setup_credentials.sh
python content_automation/test_setup.py
```

**Azure setup:**
```bash
az login
az ad sp create-for-rbac --name "betania-automation" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --sdk-auth
```

**GitHub secrets:**
Repository → Settings → Secrets → Add all 9 secrets

**Done!** 🎉

---

## 📞 Need Help?

**Check credentials:**
```bash
# View .env (without showing secrets)
grep -v PASSWORD content_automation/.env | grep -v API_KEY

# Test Azure login
az account show

# Test GitHub secrets (in GitHub Actions logs)
```

**Still stuck?**
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Check [README_SETUP.md](README_SETUP.md)
- Review error messages in `test_setup.py` output

---

**Last Updated:** 2025-11-30
