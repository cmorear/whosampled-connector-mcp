"""
WhoSampled Connector - MCP server for searching WhoSampled
"""

__version__ = "0.1.0"

from .server import main, app
from .scraper import WhoSampledScraper

__all__ = ["main", "app", "WhoSampledScraper"]