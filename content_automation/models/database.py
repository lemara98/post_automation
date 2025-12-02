"""
Database models and connection
Uses WordPress database for subscribers and custom tables for content tracking
"""
import pymysql
import logging
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Database connection and operations"""

    def __init__(self):
        """Initialize database connection"""
        self.config = {
            'host': Config.WORDPRESS_DB_HOST,
            'user': Config.WORDPRESS_DB_USER,
            'password': Config.WORDPRESS_DB_PASSWORD,
            'database': Config.WORDPRESS_DB_NAME,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        connection = pymysql.connect(**self.config)
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            connection.close()

    def init_tables(self):
        """Initialize custom tables for the automation system"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table for newsletter subscribers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(191) NOT NULL UNIQUE,
                    name VARCHAR(191),
                    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    confirmed BOOLEAN DEFAULT FALSE,
                    confirmation_token VARCHAR(64),
                    unsubscribe_token VARCHAR(64) UNIQUE,
                    active BOOLEAN DEFAULT TRUE,
                    INDEX idx_email (email),
                    INDEX idx_active (active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Table for published articles tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS published_articles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    source_url VARCHAR(255) UNIQUE,
                    wordpress_post_id INT,
                    wordpress_url VARCHAR(255),
                    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source_name VARCHAR(191),
                    tags TEXT,
                    INDEX idx_source_url (source_url),
                    INDEX idx_published_at (published_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Table for LinkedIn queue
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS linkedin_queue (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    article_id INT,
                    post_content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    posted BOOLEAN DEFAULT FALSE,
                    posted_at DATETIME,
                    INDEX idx_posted (posted),
                    FOREIGN KEY (article_id) REFERENCES published_articles(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            # Table for newsletter sends
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS newsletter_sends (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subject VARCHAR(500),
                    article_ids TEXT,
                    recipient_count INT,
                    INDEX idx_sent_at (sent_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)

            logger.info("✓ Database tables initialized")

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("✓ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {str(e)}")
            return False


class SubscriberModel:
    """Model for newsletter subscribers"""

    def __init__(self, db: Database):
        self.db = db

    def add_subscriber(
        self,
        email: str,
        name: str = None,
        confirmation_token: str = None,
        unsubscribe_token: str = None
    ) -> int:
        """
        Add a new subscriber

        Args:
            email: Subscriber email
            name: Subscriber name (optional)
            confirmation_token: Token for email confirmation
            unsubscribe_token: Token for unsubscribe link

        Returns:
            Subscriber ID
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Generate tokens if not provided
            import secrets
            confirmation_token = confirmation_token or secrets.token_urlsafe(32)
            unsubscribe_token = unsubscribe_token or secrets.token_urlsafe(32)

            cursor.execute("""
                INSERT INTO newsletter_subscribers
                (email, name, confirmation_token, unsubscribe_token)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, (email, name, confirmation_token, unsubscribe_token))

            subscriber_id = cursor.lastrowid or self.get_subscriber_by_email(email)['id']
            logger.info(f"✓ Added subscriber: {email}")
            return subscriber_id

    def confirm_subscriber(self, confirmation_token: str) -> bool:
        """Confirm subscriber email"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE newsletter_subscribers
                SET confirmed = TRUE
                WHERE confirmation_token = %s
            """, (confirmation_token,))

            if cursor.rowcount > 0:
                logger.info(f"✓ Subscriber confirmed")
                return True
            return False

    def unsubscribe(self, unsubscribe_token: str) -> bool:
        """Unsubscribe a user"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE newsletter_subscribers
                SET active = FALSE
                WHERE unsubscribe_token = %s
            """, (unsubscribe_token,))

            if cursor.rowcount > 0:
                logger.info(f"✓ Subscriber unsubscribed")
                return True
            return False

    def get_active_subscribers(self) -> List[Dict]:
        """Get all active, confirmed subscribers"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, name, subscribed_at
                FROM newsletter_subscribers
                WHERE active = TRUE AND confirmed = TRUE
            """)
            return cursor.fetchall()

    def get_subscriber_by_email(self, email: str) -> Optional[Dict]:
        """Get subscriber by email"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM newsletter_subscribers WHERE email = %s
            """, (email,))
            return cursor.fetchone()


class ArticleModel:
    """Model for published articles"""

    def __init__(self, db: Database):
        self.db = db

    def add_article(
        self,
        title: str,
        source_url: str,
        wordpress_post_id: int = None,
        wordpress_url: str = None,
        source_name: str = None,
        tags: List[str] = None
    ) -> int:
        """Add a published article to tracking"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            tags_str = ','.join(tags) if tags else None

            cursor.execute("""
                INSERT INTO published_articles
                (title, source_url, wordpress_post_id, wordpress_url, source_name, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    wordpress_post_id = VALUES(wordpress_post_id),
                    wordpress_url = VALUES(wordpress_url)
            """, (title, source_url, wordpress_post_id, wordpress_url, source_name, tags_str))

            article_id = cursor.lastrowid or self.get_article_by_url(source_url)['id']
            logger.info(f"✓ Tracked article: {title}")
            return article_id

    def get_article_by_url(self, source_url: str) -> Optional[Dict]:
        """Get article by source URL"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM published_articles WHERE source_url = %s
            """, (source_url,))
            return cursor.fetchone()

    def is_article_published(self, source_url: str) -> bool:
        """Check if article was already published"""
        return self.get_article_by_url(source_url) is not None

    def get_recent_articles(self, days: int = 7) -> List[Dict]:
        """Get articles published in the last N days"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM published_articles
                WHERE published_at > DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY published_at DESC
            """, (days,))
            return cursor.fetchall()


class LinkedInQueueModel:
    """Model for LinkedIn post queue"""

    def __init__(self, db: Database):
        self.db = db

    def add_to_queue(self, article_id: int, post_content: str) -> int:
        """Add a LinkedIn post to the queue"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO linkedin_queue (article_id, post_content)
                VALUES (%s, %s)
            """, (article_id, post_content))

            queue_id = cursor.lastrowid
            logger.info(f"✓ Added to LinkedIn queue: {queue_id}")
            return queue_id

    def get_pending_posts(self, limit: int = 10) -> List[Dict]:
        """Get pending LinkedIn posts"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lq.*, pa.title, pa.wordpress_url
                FROM linkedin_queue lq
                LEFT JOIN published_articles pa ON lq.article_id = pa.id
                WHERE lq.posted = FALSE
                ORDER BY lq.created_at DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()

    def mark_as_posted(self, queue_id: int):
        """Mark a LinkedIn post as posted"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE linkedin_queue
                SET posted = TRUE, posted_at = NOW()
                WHERE id = %s
            """, (queue_id,))
            logger.info(f"✓ Marked LinkedIn post as posted: {queue_id}")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = Database()

    if db.test_connection():
        print("✓ Database connection successful")

        # Initialize tables
        db.init_tables()

        # Test subscriber model
        subscriber_model = SubscriberModel(db)
        subscriber_id = subscriber_model.add_subscriber(
            email="test@example.com",
            name="Test User"
        )
        print(f"✓ Added subscriber: {subscriber_id}")

        # Get active subscribers
        subscribers = subscriber_model.get_active_subscribers()
        print(f"✓ Active subscribers: {len(subscribers)}")
    else:
        print("✗ Database connection failed")
