"""
Add test subscriber to newsletter database
Run this to add mile.knezevic98@gmail.com as a confirmed test subscriber
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.database import Database, SubscriberModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Add test subscriber"""
    try:
        # Initialize database
        db = Database()
        subscriber_model = SubscriberModel(db)

        # Test email
        test_email = "mile.knezevic98@gmail.com"
        test_name = "Milan Knezevic"

        logger.info(f"Adding test subscriber: {test_email}")

        # Add subscriber
        subscriber_id = subscriber_model.add_subscriber(
            email=test_email,
            name=test_name
        )

        # Get the subscriber to confirm the token
        subscriber = subscriber_model.get_subscriber_by_email(test_email)

        if subscriber:
            # Auto-confirm for testing (skip double opt-in)
            confirmed = subscriber_model.confirm_subscriber(subscriber['confirmation_token'])

            if confirmed:
                logger.info(f"✅ Test subscriber added and confirmed!")
                logger.info(f"   Email: {test_email}")
                logger.info(f"   Name: {test_name}")
                logger.info(f"   ID: {subscriber_id}")
            else:
                logger.error(f"❌ Failed to confirm subscriber")
        else:
            logger.error(f"❌ Failed to retrieve subscriber after adding")

        # Show all active subscribers
        active_subs = subscriber_model.get_active_subscribers()
        logger.info(f"\n📋 Total active subscribers: {len(active_subs)}")
        for sub in active_subs:
            logger.info(f"   - {sub['email']} ({sub['name']})")

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
