
import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def _sync_send_email(body: str, recipients: List[str], sender: str, app_password: str, subject: str = "Wieści Dnia") -> None:
    """Synchronous email sending via Gmail SMTP."""
    if not recipients:
        raise ValueError("No recipients specified")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    html_part = MIMEText(body, 'html')
    msg.attach(html_part)
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, recipients, msg.as_string())
        logger.info(f"Email sent to {len(recipients)} recipients")
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise

async def send_email(body: str, recipients: List[str], sender: str, app_password: str, subject: str = "Wieści Dnia") -> None:
    """Async wrapper for email sending."""
    await asyncio.to_thread(_sync_send_email, body, recipients, sender, app_password, subject)