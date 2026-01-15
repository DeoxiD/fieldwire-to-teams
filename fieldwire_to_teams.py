#!/usr/bin/env python3
"""Main application: Fieldwire to Teams integration."""
import os
import logging
import schedule
import time
from dotenv import load_dotenv
from modules.auth import FieldwireAuth
from modules.fetch import FieldwireFetch
from modules.card import AdaptiveCardGenerator
from modules.send import TeamsWebhookSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class FieldwireToTeamsIntegration:
    """Main integration class orchestrating the full workflow."""

    def __init__(self):
        """Initialize the integration."""
        self.api_token = os.getenv('FIELDWIRE_API_TOKEN')
        self.region = os.getenv('FIELDWIRE_REGION', 'us')
        self.project_ids = os.getenv('FIELDWIRE_PROJECT_IDS', 'ALL').split(',')
        self.webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
        self.poll_minutes = int(os.getenv('POLL_MINUTES', '60'))
        
        if not self.api_token or not self.webhook_url:
            raise ValueError("Missing required env vars: FIELDWIRE_API_TOKEN or TEAMS_WEBHOOK_URL")
        
        self.auth = FieldwireAuth(self.api_token, self.region)
        self.fetch = FieldwireFetch(self.auth)
        self.card_gen = AdaptiveCardGenerator()
        self.sender = TeamsWebhookSender(self.webhook_url)

    def process_tasks(self):
        """Main task processing logic."""
        try:
            logger.info("Starting task sync...")
            
            projects = self.fetch.get_projects(self.project_ids)
            if not projects:
                logger.warning("No projects found")
                return
            
            all_cards = []
            for project in projects:
                tasks = self.fetch.get_tasks(project.get('id'), self.poll_minutes)
                for task in tasks:
                    attachments = self.fetch.get_task_attachments(
                        project.get('id'), task.get('id')
                    )
                    card = self.card_gen.generate_task_card(task, attachments)
                    all_cards.append(card)
            
            if all_cards:
                results = self.sender.send_batch(all_cards)
                logger.info(f"Sent {results['success']} cards, {results['failed']} failed")
            else:
                logger.info("No new tasks to send")
                
        except Exception as e:
            logger.error(f"Error in process_tasks: {e}")

    def start_scheduler(self):
        """Start the scheduler for periodic polling."""
        schedule.every(self.poll_minutes).minutes.do(self.process_tasks)
        logger.info(f"Scheduler started: polling every {self.poll_minutes} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    def test_webhook(self):
        """Test webhook connectivity."""
        logger.info("Testing webhook...")
        if self.sender.test_webhook():
            logger.info("Webhook test successful!")
        else:
            logger.error("Webhook test failed!")


if __name__ == '__main__':
    import sys
    
    try:
        integration = FieldwireToTeamsIntegration()
        
        if '--test-webhook' in sys.argv:
            integration.test_webhook()
        elif '--dry-run' in sys.argv:
            logger.info("Running in dry-run mode...")
            integration.process_tasks()
        else:
            integration.start_scheduler()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
