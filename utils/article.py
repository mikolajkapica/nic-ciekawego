from dataclasses import dataclass


@dataclass
class Article():
    text: str
    url: str
    category: str