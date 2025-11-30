"""
RSS Feed Aggregator Service
Fetches and parses articles from multiple RSS feeds
"""
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Represents a fetched article"""
    title: str
    url: str
    summary: str
    published_date: datetime
    source: str
    content: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class RSSAggregator:
    """Aggregates articles from multiple RSS feeds"""

    def __init__(self, feed_urls: List[str]):
        """
        Initialize the aggregator with feed URLs

        Args:
            feed_urls: List of RSS feed URLs to monitor
        """
        self.feed_urls = feed_urls

    def fetch_articles(
        self,
        max_age_hours: int = 24,
        max_articles: int = 50
    ) -> List[Article]:
        """
        Fetch articles from all feeds

        Args:
            max_age_hours: Only fetch articles newer than this (default: 24 hours)
            max_articles: Maximum number of articles to return

        Returns:
            List of Article objects, sorted by published date (newest first)
        """
        all_articles = []
        cutoff_date = datetime.now() - timedelta(hours=max_age_hours)

        for feed_url in self.feed_urls:
            try:
                articles = self._fetch_feed(feed_url, cutoff_date)
                all_articles.extend(articles)
                logger.info(f"✓ Fetched {len(articles)} articles from {feed_url}")
            except Exception as e:
                logger.error(f"✗ Error fetching {feed_url}: {str(e)}")
                continue

        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x.published_date, reverse=True)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        logger.info(f"📰 Total articles fetched: {len(unique_articles)}")
        return unique_articles[:max_articles]

    def _fetch_feed(self, feed_url: str, cutoff_date: datetime) -> List[Article]:
        """
        Fetch and parse a single RSS feed

        Args:
            feed_url: URL of the RSS feed
            cutoff_date: Only include articles published after this date

        Returns:
            List of Article objects from this feed
        """
        feed = feedparser.parse(feed_url)
        articles = []

        feed_title = feed.feed.get('title', feed_url)

        for entry in feed.entries:
            try:
                # Parse published date
                published_date = self._parse_date(entry)

                # Skip old articles
                if published_date < cutoff_date:
                    continue

                # Extract article data
                article = Article(
                    title=entry.get('title', 'No Title'),
                    url=entry.get('link', ''),
                    summary=self._clean_html(entry.get('summary', entry.get('description', ''))),
                    published_date=published_date,
                    source=feed_title,
                    author=entry.get('author', None),
                    tags=self._extract_tags(entry)
                )

                articles.append(article)

            except Exception as e:
                logger.warning(f"Failed to parse entry from {feed_url}: {str(e)}")
                continue

        return articles

    def _parse_date(self, entry: Dict) -> datetime:
        """Parse publication date from RSS entry"""
        # Try different date fields
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                time_tuple = getattr(entry, field)
                return datetime(*time_tuple[:6])

        # Fallback to current time if no date found
        return datetime.now()

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""

        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # Limit length
        if len(text) > 500:
            text = text[:497] + "..."

        return text

    def _extract_tags(self, entry: Dict) -> List[str]:
        """Extract tags/categories from RSS entry"""
        tags = []

        if hasattr(entry, 'tags'):
            tags.extend([tag.get('term', '') for tag in entry.tags if tag.get('term')])

        if hasattr(entry, 'categories'):
            tags.extend(entry.categories)

        return list(set(tags))  # Remove duplicates

    def fetch_article_content(self, url: str) -> Optional[str]:
        """
        Fetch full article content from URL (optional enhancement)

        Args:
            url: Article URL

        Returns:
            Full article text or None if failed
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()

            # Try to find main content
            article_content = None
            for selector in ['article', 'main', '.post-content', '.article-content']:
                article_content = soup.select_one(selector)
                if article_content:
                    break

            if article_content:
                text = article_content.get_text(separator='\n', strip=True)
                return text
            else:
                # Fallback to body
                return soup.body.get_text(separator='\n', strip=True) if soup.body else None

        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    from config import Config

    aggregator = RSSAggregator(Config.RSS_FEEDS)
    articles = aggregator.fetch_articles(max_age_hours=48, max_articles=10)

    print(f"\n📰 Found {len(articles)} recent articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   URL: {article.url}")
        print(f"   Published: {article.published_date}")
        print(f"   Summary: {article.summary[:100]}...")
        print()
