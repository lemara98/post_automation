# Betania Content Automation

Automated .NET blog content system for [betania.io](https://betania.io)

## What It Does

1. **Fetches** articles from high-quality .NET blogs (Code Maze, Andrew Lock, Microsoft .NET Blog, etc.)
2. **Generates** blog posts using AI (GPT-4o-mini)
3. **Publishes** automatically to WordPress as drafts
4. **Creates** LinkedIn posts for manual review
5. **Sends** weekly newsletter to subscribers

## How to Run

### 1. Setup (First Time Only)

```bash
# Install Python dependencies
cd content_automation
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
nano .env  # Add your API keys
```

**Required credentials in `.env`:**
- `OPENAI_API_KEY` - From https://platform.openai.com/api-keys
- `WORDPRESS_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_PASSWORD`
- `WORDPRESS_DB_HOST`, `WORDPRESS_DB_NAME`, `WORDPRESS_DB_USER`, `WORDPRESS_DB_PASSWORD`
- `SENDGRID_API_KEY` - From https://sendgrid.com/

### 2. Run Daily Content Generation

```bash
source venv/bin/activate
cd content_automation
python functions/daily_content/__init__.py
```

This will:
- Fetch latest articles from RSS feeds
- Generate 5 blog posts with AI
- Publish to WordPress as drafts
- Create LinkedIn posts in database

### 3. Run Weekly Newsletter

```bash
source venv/bin/activate
cd content_automation
python functions/weekly_newsletter/__init__.py
```

This will:
- Select top 5 articles of the week
- Generate newsletter email
- Send to all subscribers

## Test Everything

```bash
source venv/bin/activate
cd content_automation
python test_setup.py
```

## RSS Feeds

Currently scraping:
- Code Maze (.NET tutorials)
- Andrew Lock (ASP.NET Core internals)
- Microsoft .NET Blog (official updates)
- Scott Hanselman (.NET & Web)
- Stephen Cleary (async/await)
- Reddit r/dotnet & r/csharp

Edit feeds in `content_automation/config.py`

## Tech Stack

- Python 3.10+
- OpenAI GPT-4o-mini
- WordPress REST API
- SendGrid (email)
- MySQL (subscribers)

## Deployment

For automated runs, deploy to Azure Functions (see `terraform/` folder) or set up cron jobs.

## Cost

- OpenAI: ~$5-10/month (depending on usage)
- SendGrid: Free (up to 100 emails/day)
- Azure Functions: Free tier available

---

Made with ❤️ for .NET developers
