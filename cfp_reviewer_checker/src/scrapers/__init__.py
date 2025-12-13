"""Scrapers package for fetching historical talks."""

from .conference_detector import ConferenceDetector
from .parallel_crawler import ParallelCrawler
from .platform_adapters import SchedAdapter, SessionizeAdapter, PlatformAdapter

__all__ = [
    "ConferenceDetector",
    "ParallelCrawler",
    "SchedAdapter",
    "SessionizeAdapter",
    "PlatformAdapter",
]

