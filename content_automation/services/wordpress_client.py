"""
WordPress API Client
Handles posting content to WordPress via REST API
"""
import logging
import requests
from typing import Dict, List, Optional
from base64 import b64encode
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WordPressClient:
    """Client for WordPress REST API"""

    def __init__(
        self,
        url: str = None,
        username: str = None,
        password: str = None,
        jwt_token: str = None
    ):
        """
        Initialize WordPress client

        Args:
            url: WordPress site URL (e.g., https://betania.io)
            username: WordPress admin username
            password: Application password (not account password!)
            jwt_token: Optional JWT token instead of username/password
        """
        self.url = (url or Config.WORDPRESS_URL).rstrip('/')
        self.api_url = f"{self.url}/wp-json/wp/v2"

        # Authentication
        if jwt_token or Config.WORDPRESS_JWT_TOKEN:
            self.headers = {
                "Authorization": f"Bearer {jwt_token or Config.WORDPRESS_JWT_TOKEN}",
                "Content-Type": "application/json"
            }
        else:
            # Use application password (Basic Auth)
            username = username or Config.WORDPRESS_USERNAME
            password = password or Config.WORDPRESS_PASSWORD

            credentials = b64encode(f"{username}:{password}".encode()).decode()
            self.headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/json"
            }

        logger.info(f"✓ WordPress client initialized for {self.url}")

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "publish",
        excerpt: str = "",
        tags: List[str] = None,
        categories: List[str] = None,
        featured_image_url: str = None
    ) -> Dict:
        """
        Create a new WordPress post

        Args:
            title: Post title
            content: Post content (HTML or markdown)
            status: Post status ('publish', 'draft', 'pending')
            excerpt: Post excerpt
            tags: List of tag names
            categories: List of category names
            featured_image_url: URL of featured image

        Returns:
            Created post data from WordPress
        """
        # Prepare post data
        post_data = {
            "title": title,
            "content": content,
            "status": status,
            "excerpt": excerpt,
        }

        # Add tags
        if tags:
            tag_ids = self._get_or_create_tags(tags)
            post_data["tags"] = tag_ids

        # Add categories
        if categories:
            category_ids = self._get_or_create_categories(categories)
            post_data["categories"] = category_ids

        try:
            response = requests.post(
                f"{self.api_url}/posts",
                headers=self.headers,
                json=post_data,
                timeout=30
            )
            response.raise_for_status()

            post = response.json()
            post_id = post["id"]
            post_url = post["link"]

            logger.info(f"✓ Created WordPress post: {title}")
            logger.info(f"  URL: {post_url}")
            logger.info(f"  ID: {post_id}")

            # Set featured image if provided
            if featured_image_url:
                self._set_featured_image(post_id, featured_image_url)

            return post

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to create post: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"  Response: {e.response.text}")
            raise

    def create_draft_post(
        self,
        title: str,
        content: str,
        excerpt: str = "",
        tags: List[str] = None
    ) -> Dict:
        """Create a draft post (for review before publishing)"""
        return self.create_post(
            title=title,
            content=content,
            status="draft",
            excerpt=excerpt,
            tags=tags
        )

    def update_post(
        self,
        post_id: int,
        title: str = None,
        content: str = None,
        status: str = None,
        **kwargs
    ) -> Dict:
        """
        Update an existing post

        Args:
            post_id: WordPress post ID
            title: New title (optional)
            content: New content (optional)
            status: New status (optional)
            **kwargs: Other fields to update

        Returns:
            Updated post data
        """
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            update_data["content"] = content
        if status:
            update_data["status"] = status
        update_data.update(kwargs)

        try:
            response = requests.post(
                f"{self.api_url}/posts/{post_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            response.raise_for_status()

            post = response.json()
            logger.info(f"✓ Updated WordPress post ID: {post_id}")
            return post

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to update post: {str(e)}")
            raise

    def _get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """Get or create tags and return their IDs"""
        tag_ids = []

        for tag_name in tag_names:
            # Search for existing tag
            try:
                response = requests.get(
                    f"{self.api_url}/tags",
                    headers=self.headers,
                    params={"search": tag_name},
                    timeout=10
                )
                response.raise_for_status()
                tags = response.json()

                if tags and tags[0]["name"].lower() == tag_name.lower():
                    tag_ids.append(tags[0]["id"])
                else:
                    # Create new tag
                    response = requests.post(
                        f"{self.api_url}/tags",
                        headers=self.headers,
                        json={"name": tag_name},
                        timeout=10
                    )
                    response.raise_for_status()
                    tag_ids.append(response.json()["id"])

            except Exception as e:
                logger.warning(f"Failed to get/create tag '{tag_name}': {str(e)}")
                continue

        return tag_ids

    def _get_or_create_categories(self, category_names: List[str]) -> List[int]:
        """Get or create categories and return their IDs"""
        category_ids = []

        for category_name in category_names:
            try:
                response = requests.get(
                    f"{self.api_url}/categories",
                    headers=self.headers,
                    params={"search": category_name},
                    timeout=10
                )
                response.raise_for_status()
                categories = response.json()

                if categories and categories[0]["name"].lower() == category_name.lower():
                    category_ids.append(categories[0]["id"])
                else:
                    # Create new category
                    response = requests.post(
                        f"{self.api_url}/categories",
                        headers=self.headers,
                        json={"name": category_name},
                        timeout=10
                    )
                    response.raise_for_status()
                    category_ids.append(response.json()["id"])

            except Exception as e:
                logger.warning(f"Failed to get/create category '{category_name}': {str(e)}")
                continue

        return category_ids

    def _set_featured_image(self, post_id: int, image_url: str):
        """Set featured image for a post (placeholder - needs media upload)"""
        # Note: This requires uploading the image to WordPress media library first
        # For now, this is a placeholder
        logger.info(f"Featured image setting not implemented yet: {image_url}")
        pass

    def test_connection(self) -> bool:
        """
        Test WordPress API connection

        Returns:
            True if connection successful
        """
        try:
            response = requests.get(
                f"{self.api_url}/posts",
                headers=self.headers,
                params={"per_page": 1},
                timeout=10
            )
            response.raise_for_status()
            logger.info("✓ WordPress API connection successful")
            return True

        except Exception as e:
            logger.error(f"✗ WordPress API connection failed: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Test connection
    wp = WordPressClient()

    if wp.test_connection():
        print("\n✓ WordPress connection successful!")

        # Example: Create a test draft post
        test_post = wp.create_draft_post(
            title="Test Post from Python",
            content="<p>This is a test post created via the WordPress REST API.</p>",
            excerpt="A test post",
            tags=["python", "automation", "test"]
        )

        print(f"\n✓ Created draft post:")
        print(f"  Title: {test_post['title']['rendered']}")
        print(f"  URL: {test_post['link']}")
        print(f"  ID: {test_post['id']}")
    else:
        print("\n✗ WordPress connection failed. Check your credentials.")
