"""
Test script to verify all components are configured correctly
"""
import sys
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def test_config():
    """Test configuration"""
    print_header("Testing Configuration")
    try:
        from config import Config
        Config.validate()
        print_success("Configuration loaded successfully")
        return True
    except Exception as e:
        print_error(f"Configuration error: {str(e)}")
        print_warning("Make sure you've created .env file and filled in all required values")
        return False

def test_database():
    """Test database connection"""
    print_header("Testing Database Connection")
    try:
        from models.database import Database
        db = Database()
        if db.test_connection():
            print_success("Database connection successful")

            # Try to initialize tables
            print("\nInitializing database tables...")
            db.init_tables()
            print_success("Database tables created/verified")
            return True
        else:
            print_error("Database connection failed")
            return False
    except Exception as e:
        print_error(f"Database error: {str(e)}")
        return False

def test_wordpress():
    """Test WordPress API connection"""
    print_header("Testing WordPress Connection")
    try:
        from services.wordpress_client import WordPressClient
        wp = WordPressClient()
        if wp.test_connection():
            print_success("WordPress API connection successful")
            return True
        else:
            print_error("WordPress API connection failed")
            return False
    except Exception as e:
        print_error(f"WordPress error: {str(e)}")
        return False

def test_rss():
    """Test RSS feed fetching"""
    print_header("Testing RSS Feed Aggregation")
    try:
        from services.rss_aggregator import RSSAggregator
        from config import Config

        aggregator = RSSAggregator(Config.RSS_FEEDS[:3])  # Test first 3 feeds
        articles = aggregator.fetch_articles(max_age_hours=48, max_articles=5)

        if articles:
            print_success(f"Fetched {len(articles)} articles")
            print("\nSample articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article.title[:60]}...")
                print(f"     Source: {article.source}")
            return True
        else:
            print_warning("No articles fetched (might be normal if feeds are down)")
            return True
    except Exception as e:
        print_error(f"RSS error: {str(e)}")
        return False

def test_ai():
    """Test AI content generation"""
    print_header("Testing AI Content Generation")
    try:
        from services.ai_content_generator import AIContentGenerator

        ai = AIContentGenerator()
        print_success("AI service initialized")

        # Test with a sample article
        from services.rss_aggregator import Article
        from datetime import datetime

        sample_article = Article(
            title="Test Article: Python 3.12 Released",
            url="https://example.com/test",
            summary="Python 3.12 introduces new features and performance improvements.",
            published_date=datetime.now(),
            source="Test Source"
        )

        print("\nGenerating sample LinkedIn post...")
        linkedin_post = ai.generate_linkedin_post(sample_article)
        print_success("LinkedIn post generated")
        print(f"\n{linkedin_post[:200]}...\n")

        return True
    except Exception as e:
        print_error(f"AI error: {str(e)}")
        print_warning("Check your OpenAI/Azure OpenAI API key and quota")
        return False

def test_email():
    """Test email service (without sending)"""
    print_header("Testing Email Service")
    try:
        from services.email_service import EmailService

        email = EmailService()
        print_success("Email service initialized (SendGrid)")
        print_warning("Skipping actual email send in test mode")
        return True
    except Exception as e:
        print_error(f"Email error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        Betania Content Automation - Setup Test            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)

    results = {
        "Configuration": test_config(),
        "Database": test_database(),
        "WordPress": test_wordpress(),
        "RSS Feeds": test_rss(),
        "AI Generation": test_ai(),
        "Email Service": test_email()
    }

    # Summary
    print_header("Test Summary")
    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if result else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"  {name:.<40} {status}")

    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}\n")

    if passed == total:
        print(f"{Fore.GREEN}{'='*60}")
        print("🎉 All tests passed! Your system is ready to run.")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print("Next steps:")
        print("  1. Test manual run: python functions/daily_content/__init__.py")
        print("  2. Deploy to Azure: func azure functionapp publish <app-name>")
        print("  3. Monitor logs in Azure Portal")
        return 0
    else:
        print(f"{Fore.RED}{'='*60}")
        print("❌ Some tests failed. Please fix the issues above.")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print("Check README_SETUP.md for troubleshooting tips")
        return 1

if __name__ == "__main__":
    try:
        # Install colorama if needed
        try:
            import colorama
        except ImportError:
            print("Installing colorama for colored output...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            import colorama

        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
