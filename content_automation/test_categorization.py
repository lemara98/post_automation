"""
Test AI-based categorization of blog posts
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.ai_content_generator import AIContentGenerator
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test category suggestion with sample articles"""
    ai_gen = AIContentGenerator()

    print("=" * 70)
    print("AI CATEGORY SUGGESTION TEST")
    print("=" * 70)
    print(f"\nAvailable Categories:")
    for cat in Config.BLOG_CATEGORIES:
        print(f"  - {cat}")
    print()

    # Test cases
    test_articles = [
        {
            "title": "Boosting ASP.NET Core Performance with Minimal APIs",
            "excerpt": "Learn how to optimize your ASP.NET Core applications using Minimal APIs and reduce memory allocations."
        },
        {
            "title": "Implementing Clean Architecture in .NET 9",
            "excerpt": "A comprehensive guide to implementing Clean Architecture patterns in your .NET applications with practical examples."
        },
        {
            "title": "Deploying .NET Apps to Azure Container Apps",
            "excerpt": "Step-by-step guide for deploying containerized .NET applications to Azure Container Apps with CI/CD pipelines."
        },
        {
            "title": "Memory Optimization Techniques in C#",
            "excerpt": "Deep dive into memory allocation patterns, Span<T>, and reducing garbage collection pressure in high-performance C# applications."
        },
        {
            "title": "Building RESTful APIs with ASP.NET Core 9",
            "excerpt": "Modern approaches to building Web APIs in ASP.NET Core including routing, model binding, and validation."
        }
    ]

    print("\n🤖 Testing AI Categorization...\n")

    for i, article in enumerate(test_articles, 1):
        print(f"\n[{i}] {article['title']}")
        print(f"    Excerpt: {article['excerpt'][:80]}...")

        category = ai_gen.suggest_category(
            title=article['title'],
            content_excerpt=article['excerpt']
        )

        print(f"    ✅ Category: {category}")
        print()

    print("=" * 70)
    print("✅ Categorization test completed!")
    print()


if __name__ == "__main__":
    main()
