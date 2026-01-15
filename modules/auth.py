"""Fieldwire API Authentication Module"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class FieldwireAuth:
    """Handles JWT authentication with Fieldwire API."""
    
    BASE_URLS = {
        "us": "https://client-api.super.fieldwire.com",
        "eu": "https://client-api.fieldwire.eu"
    }
    
    def __init__(self, api_token: str, region: str = "us"):
        """
        Initialize Fieldwire authentication.
        
        Args:
            api_token: API token from Fieldwire Account Settings
            region: 'us' or 'eu' for API region
        """
        self.api_token = api_token
        self.region = region
        self.base_url = self.BASE_URLS.get(region.lower(), self.BASE_URLS["us"])
        self.access_token = None
        self.expires_at = None
    
    def get_jwt_token(self) -> Dict:
        """
        Exchange API token for JWT.
        
        Returns:
            Dictionary with access_token and expires_at
        """
        try:
            url = f"{self.base_url}/api_keys/jwt"
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            payload = {"api_token": self.api_token}
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get("access_token")
            self.expires_at = data.get("expires_at")
            
            logger.info(f"JWT token obtained. Expires at: {self.expires_at}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get JWT token: {e}")
            raise
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        if not self.access_token:
            self.get_jwt_token()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json"
        }
