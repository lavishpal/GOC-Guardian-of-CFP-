"""Parallel crawler for fetching talks from multiple platforms concurrently."""

import asyncio
from typing import List, Optional
from src.models.corpus_manager import HistoricalTalk
from src.scrapers.platform_adapters import PlatformAdapter, SchedAdapter, SessionizeAdapter


class ParallelCrawler:
    """Crawler that fetches talks from multiple platforms in parallel."""

    def __init__(self, adapters: Optional[List[PlatformAdapter]] = None):
        """
        Initialize parallel crawler.

        Args:
            adapters: List of platform adapters, or None to use defaults
        """
        self.adapters = adapters or [
            SchedAdapter(),
            SessionizeAdapter(),
        ]

    async def crawl_all(
        self, conference_identifiers: Optional[dict] = None, limit_per_platform: int = 100
    ) -> List[HistoricalTalk]:
        """
        Crawl all platforms in parallel.

        Args:
            conference_identifiers: Optional dict mapping platform names to identifiers
            limit_per_platform: Maximum talks to fetch per platform

        Returns:
            List of all historical talks from all platforms
        """
        if conference_identifiers is None:
            conference_identifiers = {}

        # Fetch from all platforms concurrently
        tasks = [
            adapter.fetch_talks(
                conference_identifiers.get(adapter.get_platform_name()),
                limit_per_platform,
            )
            for adapter in self.adapters
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        all_talks = []
        for result in results:
            if isinstance(result, list):
                all_talks.extend(result)
            elif isinstance(result, Exception):
                # Log error but continue
                pass

        return all_talks

    async def crawl_platform(
        self, platform_name: str, conference_identifier: Optional[str] = None, limit: int = 100
    ) -> List[HistoricalTalk]:
        """
        Crawl a specific platform.

        Args:
            platform_name: Name of the platform to crawl
            conference_identifier: Optional conference identifier
            limit: Maximum talks to fetch

        Returns:
            List of historical talks from the platform
        """
        adapter = next(
            (a for a in self.adapters if a.get_platform_name() == platform_name),
            None,
        )

        if not adapter:
            return []

        return await adapter.fetch_talks(conference_identifier, limit)

    async def close(self):
        """Close all adapter connections."""
        for adapter in self.adapters:
            if hasattr(adapter, "close"):
                await adapter.close()

