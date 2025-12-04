import feedparser
from typing import List, Optional
from abc import ABC, abstractmethod

from helpers.types import RSSFeedConfig

class AbstractRSSFeed(ABC):
  def __init__(self, config: Optional[RSSFeedConfig] = None):
    if config is None:
      raise ValueError('RSS feed config is required.')
    self.config = config
    self.feed = feedparser.parse(self.config.url)

  @abstractmethod
  def get_today_feeds(self) -> List[feedparser.FeedParserDict]:
    pass

  @abstractmethod
  def parse_feed(self, feed_entries: Optional[List[feedparser.FeedParserDict]] = None) -> List[dict]:
    pass


