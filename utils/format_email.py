import logging
from typing import Dict, Any

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
    stories = summaries.get("stories", [])

    html = """
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                line-height: 1.7;
                color: #23272f;
                max-width: 820px;
                margin: 40px auto;
                padding: 32px 24px 24px 24px;
                background: linear-gradient(135deg, #f8fafc 0%, #e3e9f0 100%);
                box-shadow: 0 6px 32px 0 rgba(44, 62, 80, 0.10);
                border-radius: 18px;
            }}
            h1 {{
                color: #1a2636;
                text-align: center;
                font-size: 2.4em;
                margin-bottom: 32px;
                letter-spacing: 1px;
                font-weight: 700;
                text-shadow: 0 2px 8px #e3e9f0;
            }}
            h2 {{
                color: #2d3a4a;
                padding: 14px 18px 10px 18px;
                margin-top: 36px;
                margin-bottom: 0;
                font-size: 1.25em;
                font-weight: 600;
            }}
            ul {{
                list-style-type: disc;
                padding-left: 32px;
                margin-top: 10px;
                margin-bottom: 18px;
            }}
            ul li {{
                margin-bottom: 6px;
                font-size: 1.05em;
            }}
            p {{
                margin: 10px 0;
                font-size: 1.04em;
            }}
            a {{
                color: #2563eb;
                text-decoration: none;
                border-bottom: 1px dashed #2563eb;
                transition: color 0.2s, border-bottom 0.2s;
            }}
            a:hover {{
                color: #1e40af;
                border-bottom: 1px solid #1e40af;
            }}
            img {{  
                max-width: 100%;
                height: auto;
                margin: 18px 0 10px 0;
                border-radius: 12px;
                box-shadow: 0 2px 12px 0 rgba(44, 62, 80, 0.10);
                display: block;
                margin-left: auto;
                margin-right: auto;
            }}
            .footer {{
                font-size: 0.97em;
                color: #8a99ad;
            }}
            strong {{
                color: #1a2636;
            }}
        </style>
    </head>
    <body>
        <h1>Wieści Dnia: {current_date}</h1>
    """.format(current_date=current_date)

    for i, summary in enumerate(stories, 1):
        overview = summary.get("overview", "")
        highlights = summary.get("highlights", [])
        urls = summary.get("urls", [])
        image_url = summary.get("image_url", "")
        html += """
        <h2>{}. {}</h2>
        """.format(i, overview)
        if image_url:
            html += f'    <img src="{image_url}" alt="News Image" style="max-width:100%; height:auto; margin:10px 0;">\n'
        html += """
        <ul>
        """
        for highlight in highlights:
            html += "    <li>{}</li>\n".format(highlight)
        html += "        </ul>\n"
        html += "        <p><strong>Źródła:</strong></p>\n"
        for url in urls:
            html += "        <p><a href='{}'>{}</a></p>\n".format(url, url)

    timestamp = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss UTC")
    html += """
        <p><strong>Przetworzono łącznie {} artykułów z {} źródeł.</strong></p>
        <div class="footer">
            <p>Script version: {}</p>
            <p>Generated at: {}</p>
        </div>
    </body>
    </html>
    """.format(total_articles, sources, version, timestamp)

    logger.info("Formatted email body with %d top stories", len(stories))
    return html
