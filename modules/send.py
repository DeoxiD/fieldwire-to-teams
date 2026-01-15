"""Teams webhook sending module."""
import requests
import logging
import time
from typing import Dict, List
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class TeamsWebhookSender:
    """Send messages to Microsoft Teams via Incoming Webhook."""

    def __init__(self, webhook_url: str, rate_limit: float = 0.25):
        """Initialize Teams webhook sender.
        
        Args:
            webhook_url: Microsoft Teams Incoming Webhook URL
            rate_limit: Delay in seconds between messages (avoid throttling)
        """
        self.webhook_url = webhook_url
        self.rate_limit = rate_limit
        self.session = self._create_session()
        self.last_send_time = 0

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def send_card(self, card: Dict) -> bool:
        """Send single Adaptive Card to Teams.
        
        Args:
            card: Adaptive Card dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Enforce rate limiting
            elapsed = time.time() - self.last_send_time
            if elapsed < self.rate_limit:
                time.sleep(self.rate_limit - elapsed)
            
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "contentUrl": None,
                        "content": card
                    }
                ]
            }
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            self.last_send_time = time.time()
            
            if response.status_code == 200:
                logger.info("Card sent successfully to Teams")
                return True
            elif response.status_code == 429:
                logger.warning("Rate limited by Teams, retrying...")
                return False
            elif response.status_code == 401:
                logger.error("Unauthorized: Invalid webhook URL")
                return False
            else:
                logger.error(f"Teams API error {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending card to Teams: {e}")
            return False

    def send_batch(self, cards: List[Dict]) -> Dict[str, int]:
        """Send multiple cards to Teams.
        
        Args:
            cards: List of Adaptive Card dictionaries
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}
        
        for card in cards:
            if self.send_card(card):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Batch send complete: {results['success']} sent, {results['failed']} failed")
        return results

    def test_webhook(self) -> bool:
        """Test webhook connectivity.
        
        Returns:
            True if webhook is valid, False otherwise
        """
        try:
            test_payload = {
                "type": "message",
                "text": "Fieldwire to Teams integration - Connection test"
            }
            
            response = self.session.post(
                self.webhook_url,
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Webhook test successful")
                return True
            else:
                logger.error(f"Webhook test failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook test error: {e}")
            return False
