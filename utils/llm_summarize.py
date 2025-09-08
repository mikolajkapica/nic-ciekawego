import asyncio
from dataclasses import asdict
import json
import logging
import os
from typing import Dict, List, Any

from utils.article import Article

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
PROMPT_TEMPLATE = """
You are a neutral news analyst specializing in global affairs. Analyze the following articles corpus (JSON list with fields: text, url, category).

Find the most prominent news stories (not articles but events/topics), ensuring diversity across categories (politics, economy, tech, culture, international conflicts). If there are multiple articles, eg from different sources, please talk about various ways of portrayaling the story. There should 4 polish, 3 american, 1 ukrainian and 1 dutch stories. 

For each story generate:
- Overview: 1-2 neutral sentences summarizing the key event.
- Highlights: 3-5 bullet points with facts only (no opinions, no hallucinations; stick to provided content).
- URL(s): list of urls that touched the story
- Image URL: one of the image_urls from the articles related to the story.

Safeguards: Be factual, neutral, avoid biases (political, cultural). If content is unclear, default to description. Output structured JSON: {{"stories": [{{"overview": "...", "highlights": ["...", "..."], "urls": ["...", "..."], "image_url": "..."}}], "total_articles": X, "sources": Y}}.

Corpus: {corpus_json}
"""


def _sync_llm_summarize_corpus(
    corpus: List[Article], model: str, api_key: str
) -> Dict[str, Any]:
    """Synchronous LLM call to OpenRouter."""
    if not corpus:
        logger.warning("Empty corpus for LLM")
        return {"stories": [], "total_articles": 0, "sources": 0}

    corpus_json = json.dumps([asdict(article) for article in corpus])

    with open("cache.json", "w") as f:
        json.dump(corpus_json, f)

    prompt = PROMPT_TEMPLATE.format(corpus_json=corpus_json)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,  # e.g., mistralai/mistral-7b-instruct:free
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # Low for factual output
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        logger.info(
            f"LLM summarized {len(corpus)} articles into {len(parsed.get('stories', []))} top stories"
        )
        return parsed
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return {"stories": [], "total_articles": len(corpus), "sources": 0}


async def llm_summarize_corpus(corpus: List[Article], model: str) -> Dict[str, Any]:
    """Async wrapper for LLM summarization."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        logger.error("OpenRouter API key not set")
        return {"stories": [], "total_articles": len(corpus), "sources": 0}
    return await asyncio.to_thread(_sync_llm_summarize_corpus, corpus, model, api_key)
