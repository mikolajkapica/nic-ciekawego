import logging
from typing import List, Dict

import difflib

logger = logging.getLogger(__name__)

def build_corpus(articles: List[Dict]) -> List[Dict]:
    """Build corpus as list of article dicts, deduplicate by title similarity."""
    if not articles:
        logger.warning("No articles to build corpus")
        return []
    
    unique_articles = []
    used_titles = []
    for article in articles:
        title = article['title']
        # Check similarity with existing titles
        is_duplicate = any(
            difflib.SequenceMatcher(None, title, used_title).ratio() > 0.8
            for used_title in used_titles
        )
        if not is_duplicate:
            unique_articles.append(article)
            used_titles.append(title)
    
    logger.info(f"Deduplicated corpus: {len(unique_articles)} unique from {len(articles)} total")
    return unique_articles