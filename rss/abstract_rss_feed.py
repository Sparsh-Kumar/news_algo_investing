import feedparser
from typing import List
from abc import ABC, abstractmethod
from helpers.types import RSSFeedConfig

class AbstractRSSFeed(ABC):
  def __init__(self, config: RSSFeedConfig | None = None):
    if config is None:
      raise ValueError('RSS feed config is required.')
    self.config = config
    self.feed = feedparser.parse(self.config.url)

  @abstractmethod
  def get_today_feeds(self):
    pass

  @abstractmethod
  def parse_feed(self, feed_entries: List[feedparser.FeedParserDict] | None = None):
    pass


