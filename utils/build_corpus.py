import logging
from typing import List, Dict
from utils.article import Article

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
        if not is_duplicate:
            unique_articles.append(article)
            used_titles.append(title)
    
    logger.info(f"Deduplicated corpus: {len(unique_articles)} unique from {len(articles)} total")
    return unique_articles