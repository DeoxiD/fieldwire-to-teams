"""Fieldwire API data fetching module."""
import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .auth import FieldwireAuth

logger = logging.getLogger(__name__)


class FieldwireFetch:
    """Fetch data from Fieldwire API."""

    def __init__(self, auth: FieldwireAuth):
        """Initialize Fieldwire fetch client.
        
        Args:
            auth: FieldwireAuth instance with valid JWT token
        """
        self.auth = auth
        self.base_url = f"https://api.{auth.region}.fieldwire.io/api"
        self.headers = {
            "Authorization": f"Bearer {auth.access_token}",
            "Content-Type": "application/json"
        }

    def get_projects(self, project_ids: Optional[List[str]] = None) -> List[Dict]:
        """Fetch projects from Fieldwire.
        
        Args:
            project_ids: List of specific project IDs or None for all
            
        Returns:
            List of project dictionaries
        """
        try:
            url = f"{self.base_url}/projects"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            projects = response.json().get('projects', [])
            
            if project_ids and project_ids != ['ALL']:
                projects = [p for p in projects if p.get('id') in project_ids]
            
            logger.info(f"Fetched {len(projects)} projects")
            return projects
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching projects: {e}")
            return []

    def get_tasks(self, project_id: str, minutes_back: int = 60) -> List[Dict]:
        """Fetch recent task updates from a project.
        
        Args:
            project_id: Fieldwire project ID
            minutes_back: Get updates from last N minutes
            
        Returns:
            List of task dictionaries
        """
        try:
            url = f"{self.base_url}/projects/{project_id}/tasks"
            since_time = (datetime.utcnow() - timedelta(minutes=minutes_back)).isoformat()
            
            params = {
                'updated_at_min': since_time,
                'include_deleted': False
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            tasks = response.json().get('tasks', [])
            logger.info(f"Fetched {len(tasks)} updated tasks from project {project_id}")
            return tasks
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tasks: {e}")
            return []

    def get_task_attachments(self, project_id: str, task_id: str) -> List[Dict]:
        """Fetch attachments (photos) for a task.
        
        Args:
            project_id: Fieldwire project ID
            task_id: Fieldwire task ID
            
        Returns:
            List of attachment dictionaries
        """
        try:
            url = f"{self.base_url}/projects/{project_id}/tasks/{task_id}/attachments"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            attachments = response.json().get('attachments', [])
            logger.info(f"Fetched {len(attachments)} attachments for task {task_id}")
            return attachments
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching attachments: {e}")
            return []

    def get_attachment_url(self, attachment_id: str, project_id: str) -> Optional[str]:
        """Get direct URL for attachment.
        
        Args:
            attachment_id: Fieldwire attachment ID
            project_id: Fieldwire project ID
            
        Returns:
            Direct URL to attachment or None
        """
        try:
            url = f"{self.base_url}/projects/{project_id}/attachments/{attachment_id}/media"
            response = requests.head(url, headers=self.headers, allow_redirects=True)
            response.raise_for_status()
            return response.url
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting attachment URL: {e}")
            return None
