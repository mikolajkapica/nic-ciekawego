import logging
from typing import Dict, Any, List

import pendulum

logger = logging.getLogger(__name__)


def format_email_body(
    summaries: Dict[str, Any],
    current_date: str,
    total_articles: int,
    sources: int,
    version: str = "1.0.0",
) -> str:
    """Format the HTML email body from LLM summaries."""
    top5 = summaries.get("top5", [])
    rationale = summaries.get("rationale", "Brak racjonalizacji")

    html = """
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #34495e; border-bottom: 1px solid #ddd; }}
            ul {{ list-style-type: disc; padding-left: 20px; }}
            p {{ margin: 10px 0; }}
            a {{ color: #3498db; text-decoration: none; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.9em; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>Top 5 Wieści Dnia: Podsumowanie z {current_date}</h1>
    """.format(current_date=current_date)

    for i, summary in enumerate(top5, 1):
        overview = summary.get("overview", "")
        highlights = summary.get("highlights", [])
        url = summary.get("url", "")
        html += """
        <h2>{}. {}</h2>
        <ul>
        """.format(i, overview)
        for highlight in highlights:
            html += "    <li>{}</li>\n".format(highlight)
        html += "        </ul>\n"
        html += "        <p><strong>Źródło:</strong> <a href='{}'>{}</a></p>\n".format(
            url, url
        )

    timestamp = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss UTC")
    html += """
        <p><strong>Przetworzono łącznie {} artykułów z {} źródeł.</strong></p>
        <p><strong>Racjonalizacja wyboru:</strong> {}</p>
        <div class="footer">
            <p>Script version: {}</p>
            <p>Generated at: {}</p>
            <p><a href="mailto:unsubscribe@example.com?subject=Unsubscribe from Top 5 Wieści Dnia">Unsubscribe</a></p>
        </div>
    </body>
    </html>
    """.format(total_articles, sources, rationale, version, timestamp)

    logger.info("Formatted email body with %d top stories", len(top5))
    return html
