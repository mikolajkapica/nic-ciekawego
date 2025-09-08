import asyncio
import json
import logging
import os
from typing import Dict, List, Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
PROMPT_TEMPLATE = """
You are a neutral news analyst specializing in global affairs. Analyze the following articles corpus (JSON list with fields: title, content, url, pub_date, image_url).

Scoring Criteria (0-10 scale):
- Relevance: Global impact and connection to current events (prioritize politics, economy, tech, culture, international conflicts).
- Timeliness: How recent (bonus for <24h, penalize older).
- Diversity: Ensure topic balance (e.g., not all politics).
- Newsworthiness: Public interest, factual depth, avoids sensationalism.

Steps:
1. Deduplicate similar articles (similar titles/content).
2. Score each article.
3. Select exactly the top 5 most newsworthy based on combined scores, ensuring diversity.
4. For each selected: Generate output in Polish only:
   - Overview: 1-2 neutral sentences summarizing the key event.
   - Highlights: 3-5 bullet points with facts only (no opinions, no hallucinations; stick to provided content).
   - URL: [original URL unchanged].
   - Image URL: [original image_url unchanged if present, else empty string].
5. Overall Rationale: Brief explanation in Polish for selection (e.g., "Wybrane ze względu na globalny wpływ i różnorodność tematów.").

Safeguards: Be factual, neutral, avoid biases (political, cultural). If content is unclear, default to description. Output structured JSON: {{"top5": [{{"overview": "...", "highlights": ["...", "..."], "url": "...", "image_url": "..."}}], "rationale": "...", "total_articles": X, "sources": Y}}.

Corpus: {corpus_json}
"""

def _sync_llm_summarize_corpus(corpus: List[Dict], model: str, api_key: str) -> Dict[str, Any]:
    """Synchronous LLM call to OpenRouter."""
    if not corpus:
        logger.warning("Empty corpus for LLM")
        return {"top5": [], "rationale": "", "total_articles": 0, "sources": 0}
    
    prompt = PROMPT_TEMPLATE.format(corpus_json=json.dumps(corpus))
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,  # e.g., mistralai/mistral-7b-instruct:free
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1  # Low for factual output
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        parsed = json.loads(content)
        logger.info(f"LLM summarized {len(corpus)} articles into {len(parsed.get('top5', []))} top stories")
        return parsed
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        return {"top5": [], "rationale": "Błąd przetwarzania", "total_articles": len(corpus), "sources": 0}

async def llm_summarize_corpus(corpus: List[Dict], model: str) -> Dict[str, Any]:
    """Async wrapper for LLM summarization."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        logger.error("OpenRouter API key not set")
        return {"top5": [], "rationale": "Brak klucza API", "total_articles": len(corpus), "sources": 0}
    return await asyncio.to_thread(_sync_llm_summarize_corpus, corpus, model, api_key)