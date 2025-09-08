import asyncio
import calendar
import logging
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4

from dotenv import load_dotenv
import pendulum
import yaml
from pydantic import BaseModel

# Add utils to path
sys.path.append('.')

from utils.fetch_rss import fetch_rss, filter_by_date
from utils.extract_content import extract_full_content
from utils.translate import translate_to_polish
from utils.build_corpus import build_corpus
from utils.llm_summarize import llm_summarize_corpus
from utils.format_email import format_email_body
from utils.send_email import send_email
from collections import defaultdict

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Article(BaseModel):
    """Pydantic model for article validation."""
    title: str
    content: str
    url: str
    pub_date: datetime
    category: str
    image_url: Optional[str] = None

def load_config(path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

async def main(dry_run: bool = False):
    """Main orchestrator function."""
    run_id = str(uuid4())
    logger.info(f"Daily news summarization run started. Run ID: {run_id}")
    
    try:
        config = load_config('config.yaml')
        # Load env vars with validation
        required_env = ['DEEPL_AUTH_KEY', 'OPENROUTER_API_KEY', 'GMAIL_SENDER', 'GMAIL_APP_PASSWORD']
        env_vars = {k: os.getenv(k) for k in required_env}
        missing = [k for k, v in env_vars.items() if not v]
        if missing:
            raise ValueError(f"Missing environment variables: {missing}")
        
        # Step 1: Fetch and process articles
        feeds = config['rss_feeds']
        fetch_tasks = [fetch_rss(feed['url']) for feed in feeds]
        logger.info(f"Fetching {len(feeds)} RSS feeds")
        raw_feeds = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        logger.info("RSS fetch completed")
        articles: List[Article] = []
        for i, raw_feed in enumerate(raw_feeds):
            logger.info(f"Processing feed: {feeds[i]['name']}")
            if isinstance(raw_feed, Exception):
                logger.error(f"Failed to fetch feed {feeds[i]}: {raw_feed}")
                continue
            category = feeds[i]['category']
            filtered = filter_by_date(raw_feed.entries, hours=24)
            for art in filtered:
                if getattr(art, "summary") is None:
                    raise ValueError(f"Article summary is None for {art.link}")

        #     for art in filtered:
        #         try:
        #             translated = await translate_to_polish(
        #                 art.title + "\n\n" + art.summary 
        #             )
        #             translated_title = await translate_to_polish(art.title)
        #             translated_ = await translate_to_polish(full_content)
        #             validated_art = Article(
        #                 title=translated_title,
        #                 content=translated_content,
        #                 url=art.link,
        #                 pub_date=datetime.fromtimestamp(calendar.timegm(art.published_parsed)),
        #                 category=category,
        #                 image_url=image_url
        #             )
        #             articles.append(validated_art)
        #         except Exception as e:
        #             logger.error(f"Processing article from {feeds[i]['name']}: {e}")
        
        # if not articles:
        #     logger.warning("No articles to process, skipping")
        #     return  # Simple circuit breaker

        # # Group articles by category and select
        # articles_by_category = defaultdict(list)
        # for a in articles:
        #     articles_by_category[a.category].append(a)

        # selected_articles = []
        # for cat, arts in articles_by_category.items():
        #     if not arts:
        #         continue
        #     arts_sorted = sorted(arts, key=lambda a: a.pub_date, reverse=True)
        #     if cat == 'poland':
        #         selected_articles.extend(arts_sorted[:4])
        #     elif cat == 'usa':
        #         selected_articles.extend(arts_sorted[:3])
        #     elif cat == 'ukraine':
        #         selected_articles.extend(arts_sorted[:2])
        #     elif cat == 'netherlands':
        #         selected_articles.extend(arts_sorted[:1])

        # if len(selected_articles) < 10:
        #     logger.warning(f"Only {len(selected_articles)} articles selected, less than 10")

        # articles = selected_articles  # Replace for corpus
        # unique_sources = len(articles_by_category)
        
        # # Step 2: Build corpus
        # corpus = build_corpus([{**a.model_dump(), 'pub_date': a.pub_date.isoformat(), 'image_url': a.image_url} for a in articles])
        
        # # Step 3: LLM summarize
        # summaries = await llm_summarize_corpus(corpus, config['llm_model'])
        
        # # Step 4: Format email
        # current_date = pendulum.now('UTC').in_timezone('Europe/Warsaw').format('D MMMM YYYY')
        # email_subject = config.get('email_subject', "Top 5 Wieści Dnia: Podsumowanie z {date}").format(date=current_date)
        # email_body = format_email_body(
        #     summaries, current_date,
        #     total_articles=len(articles),
        #     sources=unique_sources
        # )
        
        # # Step 5: Send email if not dry-run
        # if not dry_run:
        #     await send_email(
        #         email_body, config['recipients'],
        #         env_vars['GMAIL_SENDER'], env_vars['GMAIL_APP_PASSWORD'], email_subject
        #     )
        
        # logger.info(f"Run completed successfully. Run ID: {run_id}")
        # if dry_run:
        #     with open('email.html', 'w', encoding='utf-8') as f:
        #         f.write(email_body)
        #     logger.info("Dry run mode: No email sent.")
    
    except Exception as e:
        logger.error(f"Run failed. Run ID: {run_id}, Error: {str(e)}")
        # TODO: Implement circuit breaker or alert

if __name__ == "__main__":
    dry_run = '--dry-run' in sys.argv
    asyncio.run(main(dry_run=dry_run))