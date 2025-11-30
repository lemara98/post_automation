# Betania Content Automation System

🤖 Automated content pipeline for [betania.io](https://betania.io)

## Features

- ✅ **Daily Blog Automation** - Auto-fetch, generate, and publish tech articles
- ✅ **AI-Powered Content** - GPT-4 generates engaging blog posts and LinkedIn content
- ✅ **Weekly Newsletter** - Top 5 curated articles sent to subscribers every Sunday
- ✅ **LinkedIn Queue** - Pre-generated posts ready for manual publishing
- ✅ **WordPress Integration** - Direct publishing to betania.io
- ✅ **Email Subscriptions** - WordPress plugin for newsletter signups

## Quick Start

```bash
cd content_automation
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python test_setup.py
```

📖 **Full documentation**: See [README_SETUP.md](content_automation/README_SETUP.md)

## Architecture

```
RSS Feeds → AI (GPT-4) → WordPress + Database → Email Newsletter
                              ↓
                        LinkedIn Queue
```

## Tech Stack

- **Python 3.11+** - Core automation
- **Azure Functions** - Serverless hosting
- **OpenAI GPT-4** - Content generation
- **WordPress REST API** - Publishing
- **SendGrid** - Email delivery
- **MySQL** - Subscriber management

## Project Structure

```
content_automation/
├── services/           # Core services
│   ├── rss_aggregator.py
│   ├── ai_content_generator.py
│   ├── wordpress_client.py
│   └── email_service.py
├── functions/          # Azure Functions
│   ├── daily_content/
│   └── weekly_newsletter/
├── models/             # Database models
├── wordpress/          # WordPress plugin
└── config.py          # Configuration

```

## Deployment

### Quick Deploy (3 options)

1. **GitHub Actions** (Recommended) - See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)
2. **Azure DevOps** - See [CICD_SETUP.md](CICD_SETUP.md)
3. **Manual** - See [README_SETUP.md](README_SETUP.md)

### Infrastructure as Code

- **Terraform**: [terraform/main.tf](terraform/main.tf)
- **CI/CD**: [.github/workflows/deploy.yml](.github/workflows/deploy.yml) or [azure-pipelines.yml](azure-pipelines.yml)

## Cost

**Monthly: $15-25** (mostly OpenAI API)

- OpenAI GPT-4: $22.50 (main cost)
- Azure Functions: $0 (free tier)
- SendGrid: $0 (free tier up to 750 subscribers)
- Everything else: ~$0.01

📊 **Detailed breakdown**: [COST_BREAKDOWN.md](COST_BREAKDOWN.md)

## License

MIT
