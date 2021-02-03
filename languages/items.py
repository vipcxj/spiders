# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Source:
    url: str
    name: Optional[str]
    keyword: List[str]
    index: int


@dataclass
class LanguagesItem:
    id: int
    content: str
    lang: str
    source: Source
    spider: str


@dataclass
class TranslateItem:
    ids: List[int]
    spider: str
