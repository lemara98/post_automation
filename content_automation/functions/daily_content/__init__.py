"""
Daily Content Azure Function
Runs every day at 9:00 AM to:
1. Fetch articles from RSS feeds
2. Generate blog posts with AI
3. Publish to WordPress
4. Queue LinkedIn posts
"""
import logging
import azure.functions as func
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import Config
from services.rss_aggregator import RSSAggregator
from services.ai_content_generator import AIContentGenerator
from services.wordpress_client import WordPressClient
from models.database import Database, ArticleModel, LinkedInQueueModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(mytimer: func.TimerRequest) -> None:
    """
    Main function for daily content generation

    Args:
        mytimer: Timer trigger from Azure Functions
    """
    logger.info("🚀 Daily content generation started")

    try:
        # Initialize services
        aggregator = RSSAggregator(Config.RSS_FEEDS)
        ai_generator = AIContentGenerator()
        wp_client = WordPressClient()
        db = Database()
        article_model = ArticleModel(db)
        linkedin_model = LinkedInQueueModel(db)

        # Step 1: Fetch recent articles
        logger.info("📰 Fetching articles from RSS feeds...")
        articles = aggregator.fetch_articles(
            max_age_hours=24,
            max_articles=20
        )

        if not articles:
            logger.warning("No new articles found")
            return

        logger.info(f"✓ Found {len(articles)} articles")

        # Step 2: Filter out already published articles
        new_articles = [
            article for article in articles
            if not article_model.is_article_published(article.url)
        ]

        logger.info(f"✓ {len(new_articles)} new articles to process")

        # Step 3: Process articles (limit to MAX_ARTICLES_PER_DAY)
        processed_count = 0
        for article in new_articles[:Config.MAX_ARTICLES_PER_DAY]:
            try:
                logger.info(f"\n📝 Processing: {article.title}")

                # Generate blog post with AI
                logger.info("  🤖 Generating blog post with AI...")
                blog_post = ai_generator.generate_blog_post(article)

                # AI suggests category based on content
                logger.info("  🏷️  AI categorizing content...")
                category = ai_generator.suggest_category(
                    title=blog_post['title'],
                    content_excerpt=blog_post['excerpt']
                )

                # Publish to WordPress
                logger.info(f"  📤 Publishing to WordPress (Category: {category})...")
                wp_post = wp_client.create_post(
                    title=blog_post['title'],
                    content=blog_post['content'],
                    status='draft',  # Change to 'publish' for auto-publish
                    excerpt=blog_post['excerpt'],
                    tags=blog_post['tags'],
                    categories=[category]
                )

                # Track in database
                logger.info("  💾 Saving to database...")
                article_id = article_model.add_article(
                    title=blog_post['title'],
                    source_url=article.url,
                    wordpress_post_id=wp_post['id'],
                    wordpress_url=wp_post['link'],
                    source_name=article.source,
                    tags=blog_post['tags']
                )

                # Generate and queue LinkedIn post
                logger.info("  💼 Generating LinkedIn post...")
                linkedin_post = ai_generator.generate_linkedin_post(article)
                linkedin_model.add_to_queue(article_id, linkedin_post)

                processed_count += 1
                logger.info(f"  ✅ Successfully processed!")

            except Exception as e:
                logger.error(f"  ❌ Error processing article: {str(e)}")
                continue

        logger.info(f"\n🎉 Daily content generation completed!")
        logger.info(f"   Processed: {processed_count}/{len(new_articles)} articles")
        logger.info(f"   Published to WordPress: {processed_count}")
        logger.info(f"   Queued for LinkedIn: {processed_count}")

    except Exception as e:
        logger.error(f"❌ Fatal error in daily content generation: {str(e)}")
        raise


# For local testing
if __name__ == "__main__":
    # Simulate timer trigger
    class MockTimer:
        pass

    main(MockTimer())
