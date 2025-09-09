import asyncio
import logging
import os

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def load_config() -> dict:
    """Load configuration from YAML file."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _sync_translate_llm(text: str, model: str, api_key: str) -> str:
    """Translate text to English using LLM via OpenRouter."""
    if not text.strip():
        return text

    prompt = f"Translate the following text to English. Provide only the translated text without any additional comments or explanations:\n\n{text}"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        translated = result["choices"][0]["message"]["content"].strip()
        logger.info(f"Translated via LLM: {len(text)} chars to English")
        return translated
    except requests.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        logger.error(f"LLM translation failed: {e}, returning original")
        return text
    except Exception as e:
        logger.error(f"LLM translation failed: {e}, returning original")
        return text


def _sync_translate_to_english(text: str, model: str, api_key: str) -> str:
    """Translate text to English using LLM."""
    return _sync_translate_llm(text, model, api_key)


async def translate_to_english(text: str) -> str:
    """Async wrapper for translation using LLM."""
    config = load_config()
    model = config.get("llm_model", "sonoma-sky-alpha")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here":
        logger.error("OpenRouter API key not set")
        return text
    return await asyncio.to_thread(_sync_translate_to_english, text, model, api_key)
