"""
Test newsletter generation without sending emails
Shows what would be sent to subscribers
"""
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from services.ai_content_generator import AIContentGenerator
from models.database import Database, ArticleModel, SubscriberModel
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test newsletter generation (dry run)"""
    try:
        logger.info("📬 Testing weekly newsletter (DRY RUN - no emails will be sent)")

        # Initialize services
        ai_generator = AIContentGenerator()
        db = Database()
        article_model = ArticleModel(db)
        subscriber_model = SubscriberModel(db)

        # Step 1: Get articles from the past 7 days
        logger.info("\n📰 Fetching articles from the past week...")
        recent_articles = article_model.get_recent_articles(days=7)

        if not recent_articles:
            logger.warning("❌ No articles published in the past week")
            logger.info("💡 Run daily_content function first to generate some articles")
            return

        logger.info(f"✅ Found {len(recent_articles)} articles from the past week:")
        for article in recent_articles:
            logger.info(f"   - {article['title']}")

        # Step 2: Convert to Article objects for AI ranking
        from services.rss_aggregator import Article

        articles_for_ranking = []
        for db_article in recent_articles:
            article = Article(
                title=db_article['title'],
                url=db_article['wordpress_url'] or db_article['source_url'],
                summary='',  # We don't store summaries in DB
                published_date=db_article['published_at'],
                source=db_article.get('source_name', 'Betania.io'),
                tags=db_article.get('tags', '').split(',') if db_article.get('tags') else []
            )
            articles_for_ranking.append(article)

        # Step 3: Use AI to select top 5 articles
        logger.info(f"\n🤖 Using AI to select top {Config.MAX_NEWSLETTER_ARTICLES} articles...")
        top_articles = ai_generator.rank_articles_for_newsletter(
            articles_for_ranking,
            top_n=min(Config.MAX_NEWSLETTER_ARTICLES, len(articles_for_ranking))
        )

        logger.info(f"✅ Selected {len(top_articles)} top articles:")
        for i, article in enumerate(top_articles, 1):
            logger.info(f"   {i}. {article.title}")
            logger.info(f"      URL: {article.url}")

        # Step 4: Generate newsletter intro
        logger.info("\n✍️  Generating newsletter intro...")
        intro = ai_generator.generate_newsletter_intro(top_articles)
        logger.info(f"✅ Generated intro:\n{intro}\n")

        # Step 5: Generate weekly practice task
        logger.info("🧠 Generating weekly practice task...")
        practice_task = ai_generator.generate_practice_task(top_articles)
        logger.info(f"✅ Generated practice task:\n{practice_task}\n")

        # Step 6: Get all active subscribers
        logger.info("👥 Fetching subscribers...")
        subscribers = subscriber_model.get_active_subscribers()

        if not subscribers:
            logger.warning("⚠️  No active subscribers found")
            logger.info("💡 Run add_test_subscriber.py to add your email")
        else:
            logger.info(f"✅ Found {len(subscribers)} active subscribers:")
            for sub in subscribers:
                logger.info(f"   - {sub['email']} ({sub['name']})")

        # Step 7: Show what would be sent
        subject = f"Top {len(top_articles)} .NET News - {datetime.now().strftime('%B %d, %Y')}"

        logger.info(f"\n📧 Newsletter Preview:")
        logger.info(f"   Subject: {subject}")
        logger.info(f"   Recipients: {len(subscribers) if subscribers else 0}")
        logger.info(f"   Articles: {len(top_articles)}")

        logger.info("\n✅ Newsletter test completed successfully!")
        logger.info("💡 To send actual emails, run: python functions/weekly_newsletter/__init__.py")

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
