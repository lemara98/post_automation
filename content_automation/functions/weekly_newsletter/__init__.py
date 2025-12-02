"""
Weekly Newsletter Azure Function
Runs every Sunday at 10:00 AM to:
1. Fetch articles from the past week
2. Use AI to select top 5 articles
3. Generate newsletter email
4. Send to all subscribers
"""
import logging
import azure.functions as func
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import Config
from services.ai_content_generator import AIContentGenerator
from services.email_service import EmailService
from models.database import Database, ArticleModel, SubscriberModel
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(mytimer: func.TimerRequest) -> None:
    """
    Main function for weekly newsletter

    Args:
        mytimer: Timer trigger from Azure Functions
    """
    logger.info("📬 Weekly newsletter generation started")

    try:
        # Initialize services
        ai_generator = AIContentGenerator()
        email_service = EmailService()
        db = Database()
        article_model = ArticleModel(db)
        subscriber_model = SubscriberModel(db)

        # Step 1: Get articles from the past 7 days
        logger.info("📰 Fetching articles from the past week...")
        recent_articles = article_model.get_recent_articles(days=7)

        if not recent_articles:
            logger.warning("No articles published in the past week")
            return

        logger.info(f"✓ Found {len(recent_articles)} articles from the past week")

        # Step 2: Convert to Article objects for AI ranking
        from services.rss_aggregator import Article

        articles_for_ranking = []
        for db_article in recent_articles:
            article = Article(
                title=db_article['title'],
                url=db_article['wordpress_url'] or db_article['source_url'],
                summary=db_article.get('excerpt', ''),
                published_date=db_article['published_at'],
                source=db_article.get('source_name', 'Betania.io'),
                tags=db_article.get('tags', '').split(',') if db_article.get('tags') else []
            )
            articles_for_ranking.append(article)

        # Step 3: Use AI to select top 5 articles
        logger.info("🤖 Using AI to select top 5 articles...")
        top_articles = ai_generator.rank_articles_for_newsletter(
            articles_for_ranking,
            top_n=Config.MAX_NEWSLETTER_ARTICLES
        )

        logger.info(f"✓ Selected {len(top_articles)} top articles")
        for i, article in enumerate(top_articles, 1):
            logger.info(f"  {i}. {article.title}")

        # Step 4: Generate newsletter intro
        logger.info("✍️  Generating newsletter intro...")
        intro = ai_generator.generate_newsletter_intro(top_articles)

        # Step 4b: Generate weekly practice task
        logger.info("🧠 Generating weekly practice task...")
        practice_task = ai_generator.generate_practice_task(top_articles)

        # Step 5: Get all active subscribers
        logger.info("👥 Fetching subscribers...")
        subscribers = subscriber_model.get_active_subscribers()

        if not subscribers:
            logger.warning("No active subscribers found")
            return

        logger.info(f"✓ Found {len(subscribers)} active subscribers")

        # Step 6: Prepare email content
        newsletter_articles = [
            {
                'title': article.title,
                'summary': article.summary,
                'url': article.url,
                'source': article.source
            }
            for article in top_articles
        ]

        # Step 7: Send newsletter
        subject = f"Top {len(top_articles)} Software Engineering News - {datetime.now().strftime('%B %d, %Y')}"

        logger.info(f"📧 Sending newsletter to {len(subscribers)} subscribers...")
        sent_count = email_service.send_newsletter(
            subscribers=subscribers,
            subject=subject,
            intro=intro,
            articles=newsletter_articles,
            practice_task=practice_task
        )

        logger.info(f"\n🎉 Weekly newsletter completed!")
        logger.info(f"   Total subscribers: {len(subscribers)}")
        logger.info(f"   Emails sent: {sent_count}")
        logger.info(f"   Success rate: {sent_count/len(subscribers)*100:.1f}%")

        # Track newsletter send (optional)
        # newsletter_model.track_send(subject, article_ids, sent_count)

    except Exception as e:
        logger.error(f"❌ Fatal error in weekly newsletter: {str(e)}")
        raise


# For local testing
if __name__ == "__main__":
    # Simulate timer trigger
    class MockTimer:
        pass

    main(MockTimer())
