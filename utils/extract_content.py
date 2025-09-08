import asyncio
import logging
from typing import Optional

from newspaper import Article, ArticleException

logger = logging.getLogger(__name__)

def _sync_extract_full_content(url: str, description: str = "") -> str:
    """Synchronous article content extraction."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        content = article.text
        if len(content) > 10240:  # Skip if >10KB
            logger.warning(f"Article too large (>10KB): {url}")
            return ""
        logger.info(f"Extracted full content from {url}")
        return content
    except ArticleException as e:
        logger.error(f"Extraction failed for {url}: {str(e)}")
        return description  # Fallback to RSS description

async def extract_full_content(url: str, description: str = "") -> str:
    """Async wrapper for content extraction."""
    return await asyncio.to_thread(_sync_extract_full_content, url, description)