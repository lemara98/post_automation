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

    # Email Configuration
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "sendgrid")  # Options: "sendgrid" or "gmail"

    # SendGrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "newsletter@betania.io")
    SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Betania Tech Newsletter")

    # Gmail SMTP
    GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "newsletter@betania.io")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # App-specific password from Google
    GMAIL_FROM_NAME = os.getenv("GMAIL_FROM_NAME", "Betania Tech Newsletter")

    # Application Settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    MAX_NEWSLETTER_ARTICLES = int(os.getenv("MAX_NEWSLETTER_ARTICLES", "3"))

    # WordPress Categories
    BLOG_CATEGORIES = [
        ".NET Development",           # General .NET, ASP.NET Core, C#, web dev
        "Performance & Optimization", # Performance tips, benchmarks, tuning
        "Architecture & Patterns",    # Clean architecture, DDD, design patterns
        "Cloud & DevOps"             # Azure, deployment, CI/CD, containers
    ]

    # RSS Feeds - High-quality .NET content sources
    RSS_FEEDS = [
        # Top .NET Blogs - Clean Architecture, Patterns, Best Practices (WORKING)
        "https://code-maze.com/feed/",                          # Code Maze - .NET tutorials, EF Core, APIs ✅
        "https://andrewlock.net/rss.xml",                       # Andrew Lock - ASP.NET Core internals ✅
        "https://exceptionnotfound.net/feed/",                  # Exception Not Found - Clean code patterns ✅

        # Official Microsoft .NET (WORKING)
        "https://devblogs.microsoft.com/dotnet/feed/",          # Official .NET Blog - Updates, performance ✅

        # Additional Quality .NET Sources (WORKING)
        "https://www.meziantou.net/feed.xml",                   # Gérald Barré - .NET tips & tricks ✅
        "https://blog.stephencleary.com/feed/",                 # Stephen Cleary - Async/await expert ✅
        "https://www.hanselman.com/blog/feed/rss/",             # Scott Hanselman - .NET & Web development ✅

        # Community & Discussion (WORKING)
        "https://www.reddit.com/r/dotnet/.rss",                 # Reddit .NET community ✅
        "https://www.reddit.com/r/csharp/.rss",                 # Reddit C# community ✅

        # NOTE: These blogs may not have recent posts, but will be included when they publish:
        # - Ardalis (Steve Smith): https://ardalis.com/blog/rss.xml
        # - Khalid Abuhakmeh: https://khalidabuhakmeh.com/rss
        # - Code with Mukesh: https://codewithmukesh.com/blog/rss.xml
        # - Milan Jovanović: No RSS feed available (newsletter only)
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
