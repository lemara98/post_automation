"""
AI Content Generator Service
Uses OpenAI/Azure OpenAI to generate blog posts and summaries
"""
import logging
from typing import List, Dict, Optional
from openai import OpenAI, AzureOpenAI
from config import Config
from services.rss_aggregator import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIContentGenerator:
    """Generates content using OpenAI GPT models"""

    def __init__(self):
        """Initialize OpenAI client (Azure or standard)"""
        if Config.AZURE_OPENAI_API_KEY:
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            self.model = Config.AZURE_OPENAI_DEPLOYMENT_NAME
            logger.info("✓ Using Azure OpenAI")
        elif Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"  # Using gpt-4o-mini (cheaper and faster)
            logger.info("✓ Using OpenAI")
        else:
            raise ValueError("No OpenAI API key configured")

    def generate_blog_post(
        self,
        article: Article,
        target_audience: str = "software engineers and tech professionals"
    ) -> Dict[str, str]:
        """
        Generate a blog post from an article

        Args:
            article: Source article
            target_audience: Target audience description

        Returns:
            Dict with 'title', 'content', 'excerpt', 'tags'
        """
        prompt = f"""You are a tech content writer for betania.io, a blog for {target_audience}, with a strong focus on practical .NET development (including .NET 8/9/10), performance tuning, and real-world tips.

Your task is to write an engaging blog post based on this article:

Title: {article.title}
Source: {article.source}
URL: {article.url}
Summary: {article.summary}

Guidelines:
1. Write a catchy, SEO-friendly title (different from the original)
2. Create an engaging 800-1200 word blog post
3. Add your own insights and analysis, especially how this relates to modern .NET development where relevant
4. Use clear headings and structure (H2/H3-style markdown headings)
5. Write in a professional but conversational tone
6. Include a brief excerpt (2-3 sentences)
7. Suggest 3-5 relevant tags

Format your response as:

TITLE:
[Your title here]

EXCERPT:
[2-3 sentence excerpt]

CONTENT:
[Your blog post content with markdown formatting]

TAGS:
[tag1, tag2, tag3]

SOURCE:
[Original article link]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert tech content writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            parsed = self._parse_blog_response(content, article.url)

            logger.info(f"✓ Generated blog post: {parsed['title']}")
            return parsed

        except Exception as e:
            logger.error(f"✗ Error generating blog post: {str(e)}")
            raise

    def generate_linkedin_post(self, article: Article) -> str:
        """
        Generate a LinkedIn post from an article

        Args:
            article: Source article

        Returns:
            LinkedIn post text (ready to paste)
        """
        prompt = f"""Create a professional LinkedIn post about this article, framed for .NET developers where possible:

Title: {article.title}
Source: {article.source}
Summary: {article.summary}
URL: {article.url}

Guidelines:
1. Keep it under 200 words
2. Start with a hook that grabs attention
3. Add your professional insight or opinion
4. Include 2-3 relevant hashtags (prioritize .NET / C# / ASP.NET / performance / cloud-related tags when appropriate)
5. End with the link to the original article
6. Professional but conversational tone

Write only the post text, nothing else.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a tech professional sharing insights on LinkedIn."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            post = response.choices[0].message.content.strip()
            logger.info(f"✓ Generated LinkedIn post for: {article.title}")
            return post

        except Exception as e:
            logger.error(f"✗ Error generating LinkedIn post: {str(e)}")
            raise

    def rank_articles_for_newsletter(
        self,
        articles: List[Article],
        top_n: int = 5
    ) -> List[Article]:
        """
        Use AI to rank and select the most relevant articles for the newsletter

        Args:
            articles: List of articles to rank
            top_n: Number of top articles to return

        Returns:
            Top N articles selected by AI
        """
        # Create article summaries for AI
        article_list = "\n\n".join([
            f"[{i+1}] {article.title}\n"
            f"Source: {article.source}\n"
            f"Summary: {article.summary}\n"
            f"Tags: {', '.join(article.tags) if article.tags else 'None'}"
            for i, article in enumerate(articles)
        ])

        prompt = f"""You are selecting the top {top_n} most valuable articles for a weekly newsletter targeting software engineers, with a strong focus on .NET (including .NET 8/9/10), C#, and practical engineering tips. You may also include occasional Python, AI, or industry pieces when they are highly valuable.

Articles:
{article_list}

Select the {top_n} most valuable articles based on:
1. Relevance to .NET developers and software engineers
2. Actionable insights or learning value (tips, how-tos, concrete examples)
3. Diversity of topics (don't pick 5 articles about the same thing)
4. Timeliness and importance (new .NET releases, tooling, notable changes)
5. Quality of source

Respond with ONLY the article numbers in order of priority, separated by commas.
Example: 3, 7, 1, 12, 5
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content curator for tech professionals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )

            # Parse response
            selected_indices = [
                int(num.strip()) - 1  # Convert to 0-indexed
                for num in response.choices[0].message.content.strip().split(',')
            ]

            # Return selected articles
            selected = [articles[i] for i in selected_indices if 0 <= i < len(articles)]
            logger.info(f"✓ AI selected {len(selected)} top articles for newsletter")
            return selected[:top_n]

        except Exception as e:
            logger.error(f"✗ Error ranking articles: {str(e)}")
            # Fallback: return first N articles
            return articles[:top_n]

    def generate_newsletter_intro(self, articles: List[Article]) -> str:
        """
        Generate an engaging introduction for the newsletter

        Args:
            articles: Articles to be featured in the newsletter

        Returns:
            Newsletter introduction text
        """
        titles = "\n".join([f"- {article.title}" for article in articles])

        prompt = f"""Write a brief, engaging introduction (2-3 sentences) for a weekly tech newsletter.

This week's top articles:
{titles}

Guidelines:
1. Welcome readers warmly
2. Tease the value they'll get this week
3. Keep it conversational and enthusiastic
4. 2-3 sentences max

Write only the introduction, nothing else.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are writing a tech newsletter introduction."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=150
            )

            intro = response.choices[0].message.content.strip()
            logger.info("✓ Generated newsletter intro")
            return intro

        except Exception as e:
            logger.error(f"✗ Error generating newsletter intro: {str(e)}")
            return "Welcome to this week's edition of the Betania Tech Newsletter! Here are the top 5 stories you shouldn't miss."

    def generate_practice_task(self, articles: List[Article]) -> str:
        """
        Generate a small weekly practice task for subscribers

        The task should encourage thinking and hands-on practice,
        ideally inspired by one of the .NET-related articles.
        """
        titles = "\n".join([f"- {article.title}" for article in articles])

        prompt = f"""You are a senior .NET engineer and mentor.

Using the themes from these articles:
{titles}

Create ONE simple but interesting weekly practice task for newsletter subscribers.

Guidelines:
1. Focus on .NET (preferably .NET 8/9/10) or general software design thinking that a .NET developer can apply.
2. The task should be solvable in 20-30 minutes.
3. Make it concrete (e.g., "Create a small console app that...", "Refactor an existing method to use...", "Write a small LINQ query that...").
4. Emphasize reasoning and design, not just syntax.
5. Do NOT include the solution, only the task description.

Write 3-6 sentences. Start with a short title like: "Weekly Practice: [short description]".
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior .NET mentor creating weekly practice tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=250
            )

            task = response.choices[0].message.content.strip()
            logger.info("✓ Generated weekly practice task")
            return task

        except Exception as e:
            logger.error(f"✗ Error generating practice task: {str(e)}")
            return "Weekly Practice: Take a small piece of code you wrote recently and refactor it using a modern .NET feature (such as pattern matching, records, or LINQ). Focus on making the code easier to read and reason about, and write down what changed and why."

    def suggest_category(self, title: str, content_excerpt: str) -> str:
        """
        Use AI to suggest the best WordPress category for an article

        Args:
            title: Article title
            content_excerpt: Brief excerpt of the content

        Returns:
            Category name from Config.BLOG_CATEGORIES
        """
        from config import Config

        categories_list = "\n".join([f"- {cat}" for cat in Config.BLOG_CATEGORIES])

        prompt = f"""You are categorizing a technical blog post for a .NET development blog.

Article Title: {title}
Content Preview: {content_excerpt[:300]}

Available Categories:
{categories_list}

Rules:
- ".NET Development" includes: ASP.NET Core, C#, web APIs, Blazor, Entity Framework, general .NET features
- "Performance & Optimization" includes: benchmarks, memory optimization, speed improvements, profiling
- "Architecture & Patterns" includes: Clean Architecture, DDD, SOLID, design patterns, project structure
- "Cloud & DevOps" includes: Azure, Docker, Kubernetes, CI/CD, deployment, infrastructure

Select the MOST appropriate single category. Respond with ONLY the category name, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at categorizing technical content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )

            category = response.choices[0].message.content.strip()

            # Validate category
            if category in Config.BLOG_CATEGORIES:
                logger.info(f"✓ AI suggested category: {category}")
                return category
            else:
                logger.warning(f"AI suggested invalid category '{category}', defaulting to .NET Development")
                return ".NET Development"

        except Exception as e:
            logger.error(f"✗ Error suggesting category: {str(e)}")
            return ".NET Development"  # Default fallback

    def _parse_blog_response(self, response: str, source_url: str) -> Dict[str, str]:
        """Parse the AI-generated blog post response"""
        sections = {
            'title': '',
            'excerpt': '',
            'content': '',
            'tags': [],
            'source_url': source_url
        }

        current_section = None
        lines = response.split('\n')

        for line in lines:
            line_upper = line.strip().upper()

            if line_upper.startswith('TITLE:'):
                current_section = 'title'
                sections['title'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('EXCERPT:'):
                current_section = 'excerpt'
                sections['excerpt'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('CONTENT:'):
                current_section = 'content'
                sections['content'] = line.split(':', 1)[1].strip() if ':' in line else ''
            elif line_upper.startswith('TAGS:'):
                current_section = 'tags'
                tag_text = line.split(':', 1)[1].strip() if ':' in line else ''
                sections['tags'] = [tag.strip() for tag in tag_text.split(',') if tag.strip()]
            elif line_upper.startswith('SOURCE:'):
                current_section = None
            elif current_section and line.strip():
                if current_section == 'tags':
                    sections['tags'].extend([tag.strip() for tag in line.split(',') if tag.strip()])
                else:
                    sections[current_section] += '\n' + line

        # Clean up
        sections['title'] = sections['title'].strip()
        sections['excerpt'] = sections['excerpt'].strip()
        raw_content = sections['content'].strip()

        # Convert markdown to HTML
        from markdown import markdown
        html_body = markdown(raw_content, extensions=['extra', 'nl2br', 'sane_lists'])

        # Wrap content in nicer HTML structure for WordPress
        html_content = f"""<div class="betania-article">
<p class="lead" style="font-size: 1.2em; color: #666; margin-bottom: 2em;">{sections['excerpt']}</p>

{html_body}

<hr style="margin: 2em 0; border: none; border-top: 1px solid #eee;" />
<p style="color: #999; font-size: 0.9em;"><strong>Source:</strong> <a href="{source_url}" target="_blank" rel="noopener noreferrer">{source_url}</a></p>
</div>"""

        sections['content'] = html_content

        return sections


# Example usage
if __name__ == "__main__":
    from services.rss_aggregator import RSSAggregator
    from config import Config

    # Fetch an article
    aggregator = RSSAggregator(Config.RSS_FEEDS[:3])  # Test with first 3 feeds
    articles = aggregator.fetch_articles(max_age_hours=48, max_articles=5)

    if articles:
        # Generate content
        generator = AIContentGenerator()

        print("\n=== Blog Post Generation ===\n")
        blog_post = generator.generate_blog_post(articles[0])
        print(f"Title: {blog_post['title']}")
        print(f"Excerpt: {blog_post['excerpt']}")
        print(f"Tags: {', '.join(blog_post['tags'])}")
        print(f"\nContent preview:\n{blog_post['content'][:300]}...")

        print("\n\n=== LinkedIn Post Generation ===\n")
        linkedin_post = generator.generate_linkedin_post(articles[0])
        print(linkedin_post)

        print("\n\n=== Newsletter Ranking ===\n")
        top_articles = generator.rank_articles_for_newsletter(articles, top_n=3)
        print(f"Top {len(top_articles)} articles selected:")
        for i, article in enumerate(top_articles, 1):
            print(f"{i}. {article.title}")
