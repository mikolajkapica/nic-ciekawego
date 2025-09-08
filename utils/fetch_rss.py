import asyncio
import calendar
import logging
import time
from datetime import datetime
from typing import List

import feedparser
import pendulum
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def _sync_fetch_rss(url: str) -> feedparser.FeedParserDict:
    """Synchronous RSS fetch with retry."""
    time.sleep(1)  # Rate limit: 1 req/sec
    feed = feedparser.parse(url)
    if feed.bozo:
        raise ValueError(f"Invalid feed: {url}, Bozo exception: {feed.bozo_exception}")
    logger.info(f"Fetched RSS from {url}")
    return feed

async def fetch_rss(url: str) -> feedparser.FeedParserDict:
    """Async wrapper for RSS fetch."""
    return await asyncio.to_thread(_sync_fetch_rss, url)

def filter_by_date(entries: List, hours: int = 1) -> List:
    """Filter entries by publication date within the last hours."""
    cutoff = pendulum.now('UTC').subtract(hours=hours)
    filtered = []
    for entry in entries:
        if 'published_parsed' in entry and entry.published_parsed:
            # Assume published_parsed is in UTC
            timestamp = calendar.timegm(entry.published_parsed)
            pub_dt = pendulum.from_timestamp(timestamp, tz='UTC')
            if pub_dt > cutoff:
                filtered.append(entry)
    logger.info(f"Filtered {len(filtered)} recent articles from {len(entries)} total")
    return filtered