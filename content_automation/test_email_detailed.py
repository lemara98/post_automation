"""
Test email sending with detailed diagnostics
"""
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    """Send a simple test email with detailed logging"""
    try:
        print("=" * 60)
        print("SENDGRID EMAIL TEST")
        print("=" * 60)

        print(f"\nFrom: {Config.SENDGRID_FROM_EMAIL}")
        print(f"To: mile.knezevic98@gmail.com")
        print(f"API Key configured: {'Yes' if Config.SENDGRID_API_KEY else 'No'}")
        print(f"API Key length: {len(Config.SENDGRID_API_KEY) if Config.SENDGRID_API_KEY else 0}")

        client = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)

        message = Mail(
            from_email=Email(Config.SENDGRID_FROM_EMAIL, "Betania Test"),
            to_emails=To("mile.knezevic98@gmail.com", "Milan"),
            subject="[TEST] Betania Newsletter Test Email",
            html_content=Content("text/html", """
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h1 style="color: #667eea;">Test Email</h1>
                    <p>This is a test email from Betania content automation system.</p>
                    <p>If you received this, the email system is working correctly!</p>
                    <p><strong>Time sent:</strong> """ + str(__import__('datetime').datetime.now()) + """</p>
                </body>
                </html>
            """)
        )

        print("\n📧 Sending test email...")
        response = client.send(message)

        print(f"\n✅ SendGrid Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Body: {response.body}")

        if response.status_code in [200, 201, 202]:
            print("\n✅ Email accepted by SendGrid!")
            print("\n⚠️  If you don't receive it, check:")
            print("   1. Spam/Junk folder")
            print("   2. SendGrid sender verification")
            print("      → Go to: https://app.sendgrid.com/settings/sender_auth")
            print(f"      → Verify: {Config.SENDGRID_FROM_EMAIL}")
            print("   3. SendGrid activity feed")
            print("      → Go to: https://app.sendgrid.com/email_activity")
        else:
            print(f"\n❌ SendGrid rejected the email: {response.status_code}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
