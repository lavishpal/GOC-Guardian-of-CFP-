"""Conference Intelligence Agent for crawling and normalizing historical talks."""

from typing import List, Dict, Any, Optional
from src.models.corpus_manager import (
    CFPSubmission,
    HistoricalTalk,
    NormalizedTalk,
    CorpusManager,
)
from src.scrapers.conference_detector import ConferenceDetector
from src.scrapers.parallel_crawler import ParallelCrawler
from src.scrapers.platform_adapters import SchedAdapter, SessionizeAdapter


class ConferenceIntelligenceAgent:
    """
    Agent that crawls Sched.com and Sessionize.com,
    normalizes historical accepted talks, and stores them in the corpus manager.
    
    Uses:
    - conference_detector.py to detect conferences from CFP submissions
    - parallel_crawler.py to crawl talks from multiple platforms
    - platform_adapters.py (SchedAdapter, SessionizeAdapter) for platform-specific fetching
    - corpus_manager.py to store normalized talks
    """

    def __init__(
        self,
        crawler: Optional[ParallelCrawler] = None,
        corpus_manager: Optional[CorpusManager] = None,
        detector: Optional[ConferenceDetector] = None,
    ):
        """
        Initialize conference intelligence agent.

        Args:
            crawler: Optional parallel crawler instance
            corpus_manager: Optional corpus manager instance
            detector: Optional conference detector instance
        """
        self.detector = detector or ConferenceDetector()
        self.crawler = crawler or ParallelCrawler()
        self.corpus_manager = corpus_manager or CorpusManager()

    async def crawl_and_store(
        self,
        conference_identifiers: Optional[Dict[str, str]] = None,
        limit_per_platform: int = 100,
    ) -> Dict[str, Any]:
        """
        Crawl Sched.com and Sessionize.com, normalize talks, and store in corpus.

        Uses parallel_crawler.py to fetch from both platforms concurrently,
        then normalizes each talk and stores it using corpus_manager.py.

        Args:
            conference_identifiers: Optional dict mapping platform names to conference identifiers
                Format: {"sched": "conference_slug", "sessionize": "event_id"}
            limit_per_platform: Maximum number of talks to fetch per platform

        Returns:
            Dictionary with crawl results and statistics:
            {
                "talks_fetched": int,
                "talks_normalized": int,
                "talks_stored": int,
                "corpus_size": int,
                "platforms_crawled": List[str]
            }
        """
        # Use parallel_crawler.py to crawl both platforms in parallel
        historical_talks = await self.crawler.crawl_all(
            conference_identifiers, limit_per_platform
        )

        # Normalize and store talks using corpus_manager.py
        normalized_count = 0
        stored_count = 0
        platforms_crawled = set()

        for talk in historical_talks:
            # Track which platforms were crawled
            if talk.source:
                platforms_crawled.add(talk.source)

            # Normalize the talk (converts HistoricalTalk to NormalizedTalk format)
            normalized_talk = talk.to_normalized()

            # Store in corpus manager (stores as HistoricalTalk, normalization is for validation)
            self.corpus_manager.add_talk(talk)
            stored_count += 1

            # Validate normalized talk
            if normalized_talk.title and normalized_talk.id:
                normalized_count += 1

        return {
            "talks_fetched": len(historical_talks),
            "talks_normalized": normalized_count,
            "talks_stored": stored_count,
            "corpus_size": self.corpus_manager.get_corpus_size(),
            "platforms_crawled": list(platforms_crawled),
        }

    async def crawl_from_cfp(
        self, cfp: CFPSubmission, limit_per_platform: int = 100
    ) -> Dict[str, Any]:
        """
        Detect conferences from CFP submission and crawl relevant talks.

        Uses conference_detector.py to detect conferences, then crawls talks
        related to those conferences.

        Args:
            cfp: CFP submission to analyze
            limit_per_platform: Maximum number of talks to fetch per platform

        Returns:
            Dictionary with crawl results and statistics
        """
        # Use conference_detector.py to detect conferences
        detected_conferences = self.detector.detect_conferences(cfp)
        conference_info = self.detector.extract_conference_info(cfp)

        # Map detected conferences to platform identifiers
        # In production, this would use a mapping service or database
        conference_identifiers = {}
        if detected_conferences:
            # For now, use detected conferences as identifiers
            # Real implementation would map conference names to platform-specific IDs
            for conf in detected_conferences:
                # Try to map to both platforms
                conference_identifiers["sched"] = conf
                conference_identifiers["sessionize"] = conf

        # Crawl and store talks
        crawl_result = await self.crawl_and_store(
            conference_identifiers if conference_identifiers else None,
            limit_per_platform,
        )

        # Add conference detection info to results
        crawl_result["conference_info"] = conference_info
        crawl_result["detected_conferences"] = detected_conferences

        return crawl_result

    async def refresh_corpus(
        self,
        conference_identifiers: Optional[Dict[str, str]] = None,
        limit_per_platform: int = 100,
    ) -> Dict[str, Any]:
        """
        Refresh the corpus by crawling and storing new talks.

        Args:
            conference_identifiers: Optional dict mapping platform names to conference identifiers
            limit_per_platform: Maximum number of talks to fetch per platform

        Returns:
            Dictionary with refresh results
        """
        return await self.crawl_and_store(conference_identifiers, limit_per_platform)

    def get_corpus_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the corpus.

        Returns:
            Dictionary with corpus statistics
        """
        all_talks = self.corpus_manager.get_all_talks()
        sched_talks = self.corpus_manager.get_talks_by_source("sched")
        sessionize_talks = self.corpus_manager.get_talks_by_source("sessionize")

        return {
            "total_talks": len(all_talks),
            "sched_talks": len(sched_talks),
            "sessionize_talks": len(sessionize_talks),
            "corpus_size": self.corpus_manager.get_corpus_size(),
        }

    def get_normalized_talks(self, limit: Optional[int] = None) -> List[NormalizedTalk]:
        """
        Get normalized talks from the corpus.

        Args:
            limit: Optional limit on number of talks to return

        Returns:
            List of normalized talks
        """
        all_talks = self.corpus_manager.get_all_talks()
        if limit:
            all_talks = all_talks[:limit]

        normalized_talks = [talk.to_normalized() for talk in all_talks]
        # Filter out invalid normalized talks
        return [
            nt for nt in normalized_talks if nt.title and nt.id and nt.conference and nt.year > 0
        ]

    async def close(self):
        """Close crawler connections."""
        await self.crawler.close()

