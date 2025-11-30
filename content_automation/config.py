"""
Configuration management for content automation system
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Azure OpenAI / OpenAI
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # WordPress
    WORDPRESS_URL = os.getenv("WORDPRESS_URL", "https://betania.io")
    WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
    WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")
    WORDPRESS_JWT_TOKEN = os.getenv("WORDPRESS_JWT_TOKEN")

    # WordPress Database
    WORDPRESS_DB_HOST = os.getenv("WORDPRESS_DB_HOST")
    WORDPRESS_DB_NAME = os.getenv("WORDPRESS_DB_NAME")
    WORDPRESS_DB_USER = os.getenv("WORDPRESS_DB_USER")
    WORDPRESS_DB_PASSWORD = os.getenv("WORDPRESS_DB_PASSWORD")

    # SendGrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "newsletter@betania.io")
    SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Betania Tech Newsletter")

    # Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    MAX_ARTICLES_PER_DAY = int(os.getenv("MAX_ARTICLES_PER_DAY", "5"))
    MAX_NEWSLETTER_ARTICLES = int(os.getenv("MAX_NEWSLETTER_ARTICLES", "5"))

    # RSS Feeds - Curated for .NET, Python, AI, and Software Industry
    RSS_FEEDS = [
        # .NET Specific
        "https://devblogs.microsoft.com/dotnet/feed/",
        "https://www.infoq.com/dotnet/feed",
        "https://www.reddit.com/r/dotnet/.rss",

        # Python
        "https://www.python.org/blogs/feed/",
        "https://realpython.com/atom.xml",
        "https://www.reddit.com/r/Python/.rss",

        # AI & Machine Learning
        "https://openai.com/blog/rss/",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://blogs.microsoft.com/ai/feed/",
        "https://www.reddit.com/r/MachineLearning/.rss",

        # General Software Industry
        "https://techcrunch.com/feed/",
        "https://news.ycombinator.com/rss",
        "https://www.theverge.com/rss/index.xml",
        "https://stackoverflow.blog/feed/",
        "https://github.blog/feed/",
        "https://dev.to/feed",

        # Software Engineering
        "https://martinfowler.com/feed.atom",
        "https://www.joelonsoftware.com/feed/",
    ]

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = []

        # Check OpenAI (either Azure or OpenAI direct)
        if not cls.AZURE_OPENAI_API_KEY and not cls.OPENAI_API_KEY:
            required.append("AZURE_OPENAI_API_KEY or OPENAI_API_KEY")

        # Check WordPress
        if not cls.WORDPRESS_USERNAME or not cls.WORDPRESS_PASSWORD:
            if not cls.WORDPRESS_JWT_TOKEN:
                required.append("WORDPRESS_USERNAME and WORDPRESS_PASSWORD (or WORDPRESS_JWT_TOKEN)")

        # Check Database
        if not all([cls.WORDPRESS_DB_HOST, cls.WORDPRESS_DB_NAME,
                    cls.WORDPRESS_DB_USER, cls.WORDPRESS_DB_PASSWORD]):
            required.append("WordPress database credentials")

        if required:
            raise ValueError(f"Missing required configuration: {', '.join(required)}")

        return True


# Validate on import (except in testing)
if os.getenv("ENVIRONMENT") != "testing":
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration warning: {e}")
        print("💡 Copy .env.example to .env and fill in your credentials")
