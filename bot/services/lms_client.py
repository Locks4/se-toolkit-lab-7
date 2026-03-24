"""LMS API client for communicating with the backend service."""

import httpx


class LMSClient:
    """Client for the Learning Management System API.
    
    This client handles all communication with the LMS backend,
    including authentication and error handling.
    """
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.
        
        Args:
            base_url: The base URL of the LMS API (e.g., http://localhost:42002).
            api_key: The API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    async def health_check(self) -> bool:
        """Check if the backend service is healthy.
        
        Returns:
            True if the service is healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers,
                    timeout=5.0,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False
    
    async def get_items(self) -> list[dict]:
        """Fetch items from the LMS backend.
        
        Returns:
            List of items from the backend.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return []
    
    async def get_scores(self, lab_id: str | None = None) -> dict:
        """Fetch scores from the LMS backend.
        
        Args:
            lab_id: Optional lab ID to filter scores.
        
        Returns:
            Dictionary containing score information.
        """
        try:
            async with httpx.AsyncClient() as client:
                endpoint = f"{self.base_url}/scores/"
                if lab_id:
                    endpoint += f"?lab_id={lab_id}"
                response = await client.get(
                    endpoint,
                    headers=self._headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            return {}
    
    async def sync_pipeline(self) -> bool:
        """Trigger a data sync from the autochecker API.
        
        Returns:
            True if sync was successful, False otherwise.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pipeline/sync",
                    headers=self._headers,
                    json={},
                    timeout=30.0,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            return False
