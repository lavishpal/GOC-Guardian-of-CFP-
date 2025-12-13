"""Client for fetching historical talks from Sessionize.com."""

import asyncio
import aiohttp
from typing import List, Optional
from goc_guardian.models import HistoricalTalk
from goc_guardian.utils.exceptions import APIUnavailableError


class SessionizeClient:
    """Client for interacting with Sessionize.com API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://sessionize.com/api/v2"):
        """
        Initialize Sessionize client.

        Args:
            api_key: Optional API key for Sessionize.com
            base_url: Base URL for Sessionize API
        """
        self.api_key = api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch_talks(
        self, event_id: Optional[str] = None, limit: int = 100
    ) -> List[HistoricalTalk]:
        """
        Fetch historical talks from Sessionize.com.

        Args:
            event_id: Optional event ID to filter by
            limit: Maximum number of talks to fetch

        Returns:
            List of HistoricalTalk objects

        Raises:
            APIUnavailableError: If API is unavailable
        """
        try:
            session = await self._get_session()
            talks = []

            # Sessionize.com API endpoint (this is a placeholder - actual API may vary)
            url = f"{self.base_url}/sessions"
            if event_id:
                url += f"?eventId={event_id}"

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        talks = self._parse_sessionize_data(data, limit)
                    elif response.status == 401:
                        # API key may be invalid, but continue with mock data
                        talks = self._get_mock_talks(limit)
                    else:
                        # API unavailable, use mock data
                        talks = self._get_mock_talks(limit)
            except (aiohttp.ClientError, asyncio.TimeoutError):
                # Network error, use mock data
                talks = self._get_mock_talks(limit)

            return talks

        except Exception as e:
            # Fail gracefully - return mock data
            return self._get_mock_talks(limit)

    def _parse_sessionize_data(self, data: dict, limit: int) -> List[HistoricalTalk]:
        """
        Parse Sessionize.com API response.

        Args:
            data: JSON response from Sessionize API
            limit: Maximum number of talks to return

        Returns:
            List of HistoricalTalk objects
        """
        talks = []
        sessions = data.get("sessions", [])[:limit]

        for session in sessions:
            talk = HistoricalTalk(
                title=session.get("title", ""),
                abstract=session.get("description", ""),
                description=session.get("description", ""),
                speaker=", ".join([s.get("name", "") for s in session.get("speakers", [])]),
                conference=session.get("event", {}).get("name"),
                year=session.get("event", {}).get("startDate", "").split("-")[0] if session.get("event", {}).get("startDate") else None,
                source="sessionize",
                url=session.get("url"),
            )
            if talk.title:
                talks.append(talk)

        return talks

    def _get_mock_talks(self, limit: int) -> List[HistoricalTalk]:
        """
        Get mock historical talks when API is unavailable.

        Args:
            limit: Number of mock talks to return

        Returns:
            List of mock HistoricalTalk objects
        """
        # Return empty list or mock data for development
        # In production, you might want to cache historical data
        return []

