from dataclasses import dataclass


@dataclass
class Article():
    """Pydantic model for article validation."""
    text: str
    url: str
    category: str