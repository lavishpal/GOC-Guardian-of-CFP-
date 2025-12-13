"""Platform adapters for different conference platforms."""

import aiohttp
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.models.corpus_manager import HistoricalTalk


class PlatformAdapter(ABC):
    """Abstract base class for platform adapters."""

    @abstractmethod
    async def fetch_talks(
        self, conference_identifier: Optional[str] = None, limit: int = 100
    ) -> List[HistoricalTalk]:
        """
        Fetch talks from the platform.

        Args:
            conference_identifier: Platform-specific conference identifier
            limit: Maximum number of talks to fetch

        Returns:
            List of historical talks
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """Get the platform name."""
        pass


class SchedAdapter(PlatformAdapter):
    """Adapter for Sched.com platform."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sched adapter.

        Args:
            api_key: Optional API key for Sched.com
        """
        self.api_key = api_key
        self.base_url = "https://sched.com/api"
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

    def get_platform_name(self) -> str:
        """Get platform name."""
        return "sched"

    async def fetch_talks(
        self, conference_identifier: Optional[str] = None, limit: int = 100
    ) -> List[HistoricalTalk]:
        """Fetch talks from Sched.com."""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/events"
            if conference_identifier:
                url += f"?conference={conference_identifier}"

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data, limit)
                    else:
                        return []
            except (aiohttp.ClientError, asyncio.TimeoutError):
                return []
        except Exception:
            return []

    def _parse_response(self, data: dict, limit: int) -> List[HistoricalTalk]:
        """Parse Sched API response."""
        import uuid
        talks = []
        events = data.get("events", [])[:limit]

        for event in events:
            event_id = event.get("id") or str(uuid.uuid4())
            start_time = event.get("start_time", "")
            year = int(start_time.split("-")[0]) if start_time and "-" in start_time else None
            
            talk = HistoricalTalk(
                id=event_id,
                title=event.get("name", ""),
                abstract=event.get("description", ""),
                description=event.get("description", ""),
                speaker=event.get("speakers", [{}])[0].get("name") if event.get("speakers") else None,
                conference=event.get("conference", {}).get("name") or "",
                year=year,
                source="sched",
                url=event.get("url") or "",
                scraped_at=datetime.now(),
            )
            if talk.title:
                talks.append(talk)

        return talks


class SessionizeAdapter(PlatformAdapter):
    """Adapter for Sessionize.com platform."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sessionize adapter.

        Args:
            api_key: Optional API key for Sessionize.com
        """
        self.api_key = api_key
        self.base_url = "https://sessionize.com/api/v2"
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

    def get_platform_name(self) -> str:
        """Get platform name."""
        return "sessionize"

    async def fetch_talks(
        self, conference_identifier: Optional[str] = None, limit: int = 100
    ) -> List[HistoricalTalk]:
        """Fetch talks from Sessionize.com."""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/sessions"
            if conference_identifier:
                url += f"?eventId={conference_identifier}"

            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data, limit)
                    else:
                        return []
            except (aiohttp.ClientError, asyncio.TimeoutError):
                return []
        except Exception:
            return []

    def _parse_response(self, data: dict, limit: int) -> List[HistoricalTalk]:
        """Parse Sessionize API response."""
        import uuid
        talks = []
        sessions = data.get("sessions", [])[:limit]

        for session in sessions:
            session_id = session.get("id") or str(uuid.uuid4())
            event_data = session.get("event", {})
            start_date = event_data.get("startDate", "")
            year = int(start_date.split("-")[0]) if start_date and "-" in start_date else None
            
            talk = HistoricalTalk(
                id=session_id,
                title=session.get("title", ""),
                abstract=session.get("description", ""),
                description=session.get("description", ""),
                speaker=", ".join([s.get("name", "") for s in session.get("speakers", [])]),
                conference=event_data.get("name") or "",
                year=year,
                source="sessionize",
                url=session.get("url") or "",
                scraped_at=datetime.now(),
            )
            if talk.title:
                talks.append(talk)

        return talks

