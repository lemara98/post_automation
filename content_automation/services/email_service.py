"""
Email Service using SendGrid
Handles sending newsletters and confirmation emails
"""
import logging
from typing import List, Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Template
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Email service for newsletters and transactional emails"""

    def __init__(self):
        """Initialize SendGrid client"""
        self.client = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        self.from_email = Email(Config.SENDGRID_FROM_EMAIL, Config.SENDGRID_FROM_NAME)
        logger.info("✓ Email service initialized")

    def send_newsletter(
        self,
        subscribers: List[Dict],
        subject: str,
        intro: str,
        articles: List[Dict],
        practice_task: str | None = None
    ) -> int:
        """
        Send newsletter to all subscribers

        Args:
            subscribers: List of subscriber dicts with 'email' and 'name'
            subject: Email subject
            intro: Newsletter introduction
            articles: List of article dicts with 'title', 'summary', 'url'

        Returns:
            Number of emails sent successfully
        """
        html_content = self._generate_newsletter_html(intro, articles, practice_task)

        sent_count = 0
        failed = []

        for subscriber in subscribers:
            try:
                # Personalize unsubscribe link
                unsubscribe_url = f"{Config.WORDPRESS_URL}/unsubscribe?token={subscriber.get('unsubscribe_token', '')}"

                # Add unsubscribe link to HTML
                personalized_html = html_content + f"""
                <div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 1px solid #eee;">
                    <p style="color: #999; font-size: 12px;">
                        You're receiving this because you subscribed to Betania Tech Newsletter.<br>
                        <a href="{unsubscribe_url}" style="color: #999;">Unsubscribe</a>
                    </p>
                </div>
                """

                message = Mail(
                    from_email=self.from_email,
                    to_emails=To(subscriber['email'], subscriber.get('name')),
                    subject=subject,
                    html_content=Content("text/html", personalized_html)
                )

                response = self.client.send(message)

                if response.status_code in [200, 201, 202]:
                    sent_count += 1
                    logger.info(f"✓ Sent newsletter to {subscriber['email']}")
                else:
                    failed.append(subscriber['email'])
                    logger.warning(f"✗ Failed to send to {subscriber['email']}: {response.status_code}")

            except Exception as e:
                failed.append(subscriber['email'])
                logger.error(f"✗ Error sending to {subscriber['email']}: {str(e)}")

        logger.info(f"📧 Newsletter sent: {sent_count}/{len(subscribers)} successful")
        if failed:
            logger.warning(f"Failed recipients: {', '.join(failed)}")

        return sent_count

    def send_confirmation_email(
        self,
        email: str,
        name: str,
        confirmation_token: str
    ):
        """
        Send subscription confirmation email

        Args:
            email: Subscriber email
            name: Subscriber name
            confirmation_token: Confirmation token
        """
        confirmation_url = f"{Config.WORDPRESS_URL}/confirm-subscription?token={confirmation_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Welcome to Betania Tech Newsletter!</h1>
            </div>

            <div style="background: #fff; padding: 30px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 10px 10px;">
                <p>Hi {name or 'there'},</p>

                <p>Thanks for subscribing to the Betania Tech Newsletter! You're one step away from getting the top 5 software engineering news every week.</p>

                <p>Please confirm your email address by clicking the button below:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{confirmation_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Confirm Subscription
                    </a>
                </div>

                <p>Or copy and paste this link into your browser:</p>
                <p style="color: #667eea; word-break: break-all;">{confirmation_url}</p>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    If you didn't subscribe to this newsletter, you can safely ignore this email.
                </p>
            </div>

            <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                <p>Betania.io - Tech insights for software engineers</p>
            </div>
        </body>
        </html>
        """

        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(email, name),
                subject="Confirm your subscription to Betania Tech Newsletter",
                html_content=Content("text/html", html_content)
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Sent confirmation email to {email}")
            else:
                logger.warning(f"✗ Failed to send confirmation to {email}: {response.status_code}")

        except Exception as e:
            logger.error(f"✗ Error sending confirmation to {email}: {str(e)}")
            raise

    def _generate_newsletter_html(self, intro: str, articles: List[Dict], practice_task: str | None = None) -> str:
        """Generate HTML for newsletter"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5;">
            <!-- Header with background logo -->
            <div style="
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%),
                            url('https://raw.githubusercontent.com/yourusername/betania-assets/main/logo-bg.png') center/cover;
                background-color: #667eea;
                padding: 60px 30px;
                text-align: center;
                border-radius: 12px 12px 0 0;
                position: relative;
                overflow: hidden;
            ">
                <!-- Subtle pattern overlay -->
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDE4YzMuMzEgMCA2IDIuNjkgNiA2cy0yLjY5IDYtNiA2LTYtMi42OS02LTYgMi42OS02IDYtNiIvPjwvZz48L2c+PC9zdmc+');
                    opacity: 0.3;
                "></div>

                <!-- Logo (optional - you can add an actual logo image URL) -->
                <!-- <img src="https://betania.io/logo.png" alt="Betania" style="width: 80px; height: auto; margin-bottom: 15px; position: relative; z-index: 1;" /> -->

                <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 600; letter-spacing: -0.5px; position: relative; z-index: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    BETANIA
                </h1>
                <p style="color: rgba(255,255,255,0.95); margin: 8px 0 0 0; font-size: 15px; font-weight: 400; letter-spacing: 0.5px; position: relative; z-index: 1;">
                    Your Weekly .NET & Software Engineering Digest
                </p>
            </div>

            <div style="background: #fff; padding: 40px 30px; border: 1px solid #e5e5e5; border-top: none; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <p style="font-size: 16px; color: #555; line-height: 1.7; margin-top: 0;">{{ intro }}</p>

                <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 35px 0;">

                {% if practice_task %}
                <div style="background: linear-gradient(to right, #f8f9ff 0%, #f0f4ff 100%); border-left: 4px solid #667eea; padding: 24px; margin-bottom: 35px; border-radius: 6px;">
                    <h2 style="margin: 0 0 12px 0; font-size: 18px; color: #333; font-weight: 600;">🧠 Weekly Practice Task</h2>
                    <p style="color: #555; margin: 0; white-space: pre-line; line-height: 1.7;">{{ practice_task }}</p>
                </div>
                {% endif %}

                {% for article in articles %}
                <div style="margin-bottom: 35px; padding-bottom: 35px; border-bottom: 1px solid #f0f0f0;">
                    <div style="display: inline-block; background: #667eea; color: white; font-size: 14px; font-weight: 600; padding: 4px 12px; border-radius: 4px; margin-bottom: 12px;">
                        {{ loop.index }}
                    </div>

                    <h2 style="color: #222; margin: 0 0 10px 0; font-size: 22px; font-weight: 600; line-height: 1.3;">
                        <a href="{{ article.url }}" style="color: #222; text-decoration: none;">
                            {{ article.title }}
                        </a>
                    </h2>

                    <p style="color: #999; font-size: 13px; margin: 8px 0; font-weight: 500;">
                        📰 {{ article.source }}
                    </p>

                    <p style="color: #555; margin: 15px 0; line-height: 1.7; font-size: 15px;">
                        {{ article.summary }}
                    </p>

                    <a href="{{ article.url }}" style="
                        display: inline-block;
                        color: #667eea;
                        text-decoration: none;
                        font-weight: 600;
                        font-size: 14px;
                        padding: 10px 20px;
                        border: 2px solid #667eea;
                        border-radius: 6px;
                        transition: all 0.3s;
                    ">
                        Read Full Article →
                    </a>
                </div>
                {% endfor %}

                <div style="background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%); padding: 25px; border-radius: 8px; margin-top: 40px; text-align: center; border: 1px solid #e5e9ff;">
                    <p style="margin: 0; color: #555; font-size: 15px; line-height: 1.6;">
                        💡 <strong>Want more .NET insights?</strong><br>
                        <a href="{{ wordpress_url }}" style="color: #667eea; text-decoration: none; font-weight: 600;">Visit betania.io</a>
                    </p>
                </div>
            </div>

            <div style="background: #fff; padding: 25px; border: 1px solid #e5e5e5; border-top: none; border-radius: 0 0 12px 12px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <p style="color: #999; font-size: 13px; margin: 0; line-height: 1.6;">
                    © {{ year }} Betania.io · All rights reserved<br>
                    <span style="font-size: 11px;">Delivering quality .NET content to developers worldwide</span>
                </p>
            </div>
        </body>
        </html>
        """

        from datetime import datetime

        jinja_template = Template(template)
        html = jinja_template.render(
            intro=intro,
            articles=articles,
            practice_task=practice_task,
            wordpress_url=Config.WORDPRESS_URL,
            year=datetime.now().year
        )

        return html


# Example usage
if __name__ == "__main__":
    email_service = EmailService()

    # Test confirmation email
    print("Sending test confirmation email...")
    email_service.send_confirmation_email(
        email="test@example.com",
        name="Test User",
        confirmation_token="test_token_12345"
    )

    # Test newsletter
    print("\nSending test newsletter...")
    test_subscribers = [
        {"email": "test@example.com", "name": "Test User", "unsubscribe_token": "test_token"}
    ]

    test_articles = [
        {
            "title": ".NET 9 Released with Major Performance Improvements",
            "summary": "Microsoft announces .NET 9 with significant performance enhancements and new features...",
            "url": "https://example.com/article1",
            "source": "Microsoft DevBlogs"
        },
        {
            "title": "Python 3.13 Alpha Now Available",
            "summary": "The first alpha release of Python 3.13 introduces experimental JIT compilation...",
            "url": "https://example.com/article2",
            "source": "Python.org"
        }
    ]

    email_service.send_newsletter(
        subscribers=test_subscribers,
        subject="Top 5 Tech News This Week",
        intro="Here are this week's most important software engineering stories!",
        articles=test_articles
    )

    print("\n✓ Test emails sent!")
