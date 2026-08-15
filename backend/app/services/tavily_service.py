# backend/app/services/tavily_service.py
"""Service for integrating with the Tavily image search API.
Provides a simple method to fetch image URLs for a given query.
"""

import os
import logging
import requests
from typing import List

from backend.app.core.config import Config

logger = logging.getLogger(__name__)

class TavilyService:
    """Utility class to search for images using the Tavily API."""

    @staticmethod
    def _get_api_key() -> str:
        """Retrieve the Tavily API key from environment or config.
        Returns an empty string if not set.
        """
        return os.getenv("TAVILY_API_KEY", "")

    @staticmethod
    def search_images(query: str, top_n: int = 5) -> List[str]:
        """Search for images related to *query* and return a list of image URLs.

        Args:
            query (str): Search term, typically a crop name.
            top_n (int): Number of image results to return (default 5).

        Returns:
            List[str]: List of image URLs. Returns an empty list on failure.
        """
        api_key = TavilyService._get_api_key()
        if not api_key:
            logger.warning("TAVILY_API_KEY is not set; image search will be skipped.")
            return []

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_images": True,
            "max_results": top_n,
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Standard Tavily JSON structure returns images in root-level "images" key
            images: List[str] = data.get("images", [])
            
            # Fallback check results just in case
            if not images:
                for item in data.get("results", []):
                    img = item.get("image")
                    if img:
                        images.append(img)
            return images[:top_n]
        except Exception as e:
            logger.error(f"Tavily image search failed for query '{query}': {e}")
            return []

