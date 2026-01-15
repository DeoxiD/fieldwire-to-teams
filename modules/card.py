"""Adaptive Card generation module for Teams."""
import json
import logging
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

logger = logging.getLogger(__name__)


class AdaptiveCardGenerator:
    """Generate Microsoft Teams Adaptive Cards from task data."""

    def __init__(self, template_dir: str = "templates"):
        """Initialize card generator with Jinja2 templates.
        
        Args:
            template_dir: Directory containing card templates
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['json'])
        )

    def generate_task_card(self, task: Dict, attachments: List[Dict] = None) -> Dict:
        """Generate Adaptive Card for a Fieldwire task.
        
        Args:
            task: Task data dictionary from Fieldwire API
            attachments: List of attachment/photo dictionaries
            
        Returns:
            Card dictionary ready for Teams Webhook
        """
        try:
            template = self.env.get_template('card.json.j2')
            
            # Prepare attachment data for template
            photos = []
            if attachments:
                photos = attachments[:3]  # Limit to 3 photos
            
            # Render template with task data
            card_json = template.render(
                task_id=task.get('id'),
                task_name=task.get('title', 'Untitled Task'),
                status=task.get('status', 'unknown'),
                description=task.get('description', ''),
                due_date=task.get('due_date', ''),
                assigned_to=task.get('assigned_to', {}).get('name', 'Unassigned'),
                priority=task.get('priority', 'normal'),
                photos=photos
            )
            
            # Parse and validate JSON
            card = json.loads(card_json)
            logger.info(f"Generated card for task {task.get('id')}")
            return card
            
        except Exception as e:
            logger.error(f"Error generating card: {e}")
            return self._get_fallback_card(task)

    def _get_fallback_card(self, task: Dict) -> Dict:
        """Generate simple fallback card if template rendering fails.
        
        Args:
            task: Task data dictionary
            
        Returns:
            Simple card dictionary
        """
        return {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "size": "large",
                    "weight": "bolder",
                    "text": task.get('title', 'Task Update')
                },
                {
                    "type": "TextBlock",
                    "text": f"Status: {task.get('status', 'unknown')}",
                    "spacing": "small"
                },
                {
                    "type": "TextBlock",
                    "text": task.get('description', 'No description'),
                    "spacing": "small"
                }
            ]
        }

    def generate_batch_message(self, cards: List[Dict]) -> Dict:
        """Generate Teams message wrapper for multiple cards.
        
        Args:
            cards: List of Adaptive Card dictionaries
            
        Returns:
            Message payload for Teams Webhook
        """
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"Fieldwire Task Updates - {len(cards)} new tasks",
            "themeColor": "0078D4",
            "sections": [
                {
                    "activityTitle": "Fieldwire Task Updates",
                    "activitySubtitle": f"{len(cards)} new tasks from Fieldwire",
                    "text": "Check the cards below for details"
                }
            ]
        }
