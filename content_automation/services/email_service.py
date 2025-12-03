"""
Email Service supporting both SendGrid and Gmail SMTP
Handles sending newsletters and confirmation emails
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from jinja2 import Template
from config import Config

# Try to import SendGrid (optional)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Email service for newsletters and transactional emails"""

    def __init__(self):
        """Initialize email service (SendGrid or Gmail SMTP based on config)"""
        self.provider = Config.EMAIL_PROVIDER.lower()

        if self.provider == "gmail":
            # Gmail SMTP configuration
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.from_email_addr = Config.GMAIL_EMAIL
            self.from_name = Config.GMAIL_FROM_NAME
            self.password = Config.GMAIL_APP_PASSWORD
            logger.info("✓ Email service initialized (Gmail SMTP)")
        else:
            # SendGrid configuration
            if not SENDGRID_AVAILABLE:
                raise ImportError("SendGrid library not installed. Run: pip install sendgrid")
            self.sendgrid_client = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
            self.from_email_addr = Config.SENDGRID_FROM_EMAIL
            self.from_name = Config.SENDGRID_FROM_NAME
            logger.info("✓ Email service initialized (SendGrid)")

    def _send_email_gmail(self, to_email: str, to_name: str, subject: str, html_content: str) -> bool:
        """Send email via Gmail SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email_addr}>"
            msg['To'] = f"{to_name} <{to_email}>" if to_name else to_email
            msg['Subject'] = subject

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.from_email_addr, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            logger.error(f"Gmail SMTP error: {str(e)}")
            return False

    def _send_email_sendgrid(self, to_email: str, to_name: str, subject: str, html_content: str) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=Email(self.from_email_addr, self.from_name),
                to_emails=To(to_email, to_name),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            response = self.sendgrid_client.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return False

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

                # Send via chosen provider
                if self.provider == "gmail":
                    success = self._send_email_gmail(
                        to_email=subscriber['email'],
                        to_name=subscriber.get('name', ''),
                        subject=subject,
                        html_content=personalized_html
                    )
                else:
                    success = self._send_email_sendgrid(
                        to_email=subscriber['email'],
                        to_name=subscriber.get('name', ''),
                        subject=subject,
                        html_content=personalized_html
                    )

                if success:
                    sent_count += 1
                    logger.info(f"✓ Sent newsletter to {subscriber['email']}")
                else:
                    failed.append(subscriber['email'])

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
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">
            <!-- Header with Betania logo -->
            <div style="background: #ffffff; padding: 50px 30px 40px; text-align: center; border-bottom: 3px solid #00d4ff;">
                <!-- Inline SVG Triangle Logo -->
                <svg width="100" height="100" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 20px;">
                    <path d="M250 50 L450 400 L50 400 Z" fill="none" stroke="#00d4ff" stroke-width="6" opacity="0.25"/>
                    <path d="M250 100 L400 360 L100 360 Z" fill="none" stroke="#00d4ff" stroke-width="5" opacity="0.4"/>
                    <path d="M250 150 L350 320 L150 320 Z" fill="none" stroke="#00d4ff" stroke-width="4" opacity="0.6"/>
                    <path d="M250 200 L300 280 L200 280 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <path d="M200 280 L250 360 L150 360 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <path d="M300 280 L350 360 L250 360 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <line x1="60" y1="405" x2="440" y2="405" stroke="#00d4ff" stroke-width="1.5" opacity="0.3"/>
                </svg>

                <h1 style="color: #000000; margin: 0 0 10px 0; font-size: 38px; font-weight: 700; letter-spacing: 5px;">
                    BETANIA
                </h1>
                <p style="color: #00d4ff; margin: 0; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">
                    Welcome to the Newsletter!
                </p>
            </div>

            <div style="background: #fff; padding: 40px 30px;">
                <p style="font-size: 18px; color: #000; font-weight: 600; margin-top: 0;">Hi {name or 'there'},</p>

                <p style="font-size: 16px; color: #444; line-height: 1.8;">
                    Thanks for subscribing to the <strong>Betania Tech Newsletter</strong>! You're one step away from getting weekly .NET & software engineering insights delivered to your inbox.
                </p>

                <p style="font-size: 16px; color: #444; line-height: 1.8;">
                    Please confirm your email address by clicking the button below:
                </p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{confirmation_url}" style="
                        display: inline-block;
                        background: #00d4ff;
                        color: #000;
                        padding: 16px 48px;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 16px;
                        border: 2px solid #00d4ff;
                    ">
                        ✓ Confirm Subscription
                    </a>
                </div>

                <p style="font-size: 14px; color: #888; line-height: 1.6;">
                    Or copy and paste this link into your browser:
                </p>
                <p style="color: #00d4ff; word-break: break-all; font-size: 13px; background: #f0fdff; padding: 12px; border-radius: 4px; border: 1px solid #00d4ff;">
                    {confirmation_url}
                </p>

                <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 35px 0;">

                <p style="color: #888; font-size: 14px; line-height: 1.6;">
                    If you didn't subscribe to this newsletter, you can safely ignore this email.
                </p>
            </div>

            <div style="background: #fff; padding: 25px; text-align: center; border-top: 2px solid #f0f0f0;">
                <p style="color: #888; font-size: 13px; margin: 0; line-height: 1.6;">
                    © 2024 Betania.io · All rights reserved<br>
                    <span style="font-size: 11px; color: #aaa;">Delivering quality .NET content to developers worldwide</span>
                </p>
            </div>
        </body>
        </html>
        """

        # Send via chosen provider
        if self.provider == "gmail":
            success = self._send_email_gmail(
                to_email=email,
                to_name=name,
                subject="Confirm your subscription to Betania Tech Newsletter",
                html_content=html_content
            )
        else:
            success = self._send_email_sendgrid(
                to_email=email,
                to_name=name,
                subject="Confirm your subscription to Betania Tech Newsletter",
                html_content=html_content
            )

        if success:
            logger.info(f"✓ Sent confirmation email to {email}")
        else:
            logger.warning(f"✗ Failed to send confirmation to {email}")
            raise Exception(f"Failed to send confirmation email to {email}")

    def _generate_newsletter_html(self, intro: str, articles: List[Dict], practice_task: str | None = None) -> str:
        """Generate HTML for newsletter"""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">
            <!-- Header with Betania triangle logo -->
            <div style="background: #ffffff; padding: 50px 30px 40px; text-align: center; border-bottom: 3px solid #00d4ff;">
                <!-- Inline SVG Triangle Logo -->
                <svg width="100" height="100" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 20px;">
                    <!-- Outer triangle with tech effect -->
                    <path d="M250 50 L450 400 L50 400 Z" fill="none" stroke="#00d4ff" stroke-width="6" opacity="0.25"/>
                    <!-- Second triangle -->
                    <path d="M250 100 L400 360 L100 360 Z" fill="none" stroke="#00d4ff" stroke-width="5" opacity="0.4"/>
                    <!-- Third triangle -->
                    <path d="M250 150 L350 320 L150 320 Z" fill="none" stroke="#00d4ff" stroke-width="4" opacity="0.6"/>
                    <!-- Inner Triforce triangles -->
                    <path d="M250 200 L300 280 L200 280 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <path d="M200 280 L250 360 L150 360 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <path d="M300 280 L350 360 L250 360 Z" fill="none" stroke="#00d4ff" stroke-width="3.5" opacity="0.85"/>
                    <!-- Circuit lines -->
                    <line x1="60" y1="405" x2="440" y2="405" stroke="#00d4ff" stroke-width="1.5" opacity="0.3"/>
                </svg>

                <h1 style="color: #000000; margin: 0 0 10px 0; font-size: 38px; font-weight: 700; letter-spacing: 5px;">
                    BETANIA
                </h1>
                <p style="color: #00d4ff; margin: 0; font-size: 13px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;">
                    Your Weekly .NET & Software Engineering Digest
                </p>
            </div>

            <div style="background: #fff; padding: 40px 30px;">
                <p style="font-size: 16px; color: #444; line-height: 1.8; margin-top: 0;">{{ intro }}</p>

                <hr style="border: none; border-top: 2px solid #f0f0f0; margin: 35px 0;">

                {% if practice_task %}
                <div style="background: #f0fdff; border-left: 4px solid #00d4ff; padding: 24px; margin-bottom: 35px; border-radius: 6px;">
                    <h2 style="margin: 0 0 12px 0; font-size: 18px; color: #000; font-weight: 700;">🧠 Weekly Practice Task</h2>
                    <p style="color: #444; margin: 0; white-space: pre-line; line-height: 1.8;">{{ practice_task }}</p>
                </div>
                {% endif %}

                {% for article in articles %}
                <div style="margin-bottom: 35px; padding-bottom: 35px; border-bottom: 1px solid #f0f0f0;">
                    <div style="display: inline-block; background: #00d4ff; color: #000; font-size: 14px; font-weight: 700; padding: 5px 14px; border-radius: 4px; margin-bottom: 12px;">
                        {{ loop.index }}
                    </div>

                    <h2 style="color: #000; margin: 0 0 10px 0; font-size: 22px; font-weight: 700; line-height: 1.3;">
                        <a href="{{ article.url }}" style="color: #000; text-decoration: none;">
                            {{ article.title }}
                        </a>
                    </h2>

                    <p style="color: #888; font-size: 13px; margin: 8px 0; font-weight: 500;">
                        📰 {{ article.source }}
                    </p>

                    <p style="color: #444; margin: 15px 0; line-height: 1.8; font-size: 15px;">
                        {{ article.summary }}
                    </p>

                    <a href="{{ article.url }}" style="
                        display: inline-block;
                        color: #00d4ff;
                        text-decoration: none;
                        font-weight: 700;
                        font-size: 14px;
                        padding: 10px 24px;
                        border: 2px solid #00d4ff;
                        border-radius: 6px;
                        background: transparent;
                    ">
                        Read Full Article →
                    </a>
                </div>
                {% endfor %}

                <div style="background: #f0fdff; padding: 25px; border-radius: 8px; margin-top: 40px; text-align: center; border: 2px solid #00d4ff;">
                    <p style="margin: 0; color: #000; font-size: 15px; line-height: 1.6; font-weight: 600;">
                        💡 Want more .NET insights?<br>
                        <a href="{{ wordpress_url }}" style="color: #00d4ff; text-decoration: none; font-weight: 700;">Visit betania.io</a>
                    </p>
                </div>
            </div>

            <div style="background: #fff; padding: 25px; text-align: center; border-top: 2px solid #f0f0f0;">
                <p style="color: #888; font-size: 13px; margin: 0; line-height: 1.6;">
                    © {{ year }} Betania.io · All rights reserved<br>
                    <span style="font-size: 11px; color: #aaa;">Delivering quality .NET content to developers worldwide</span>
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
