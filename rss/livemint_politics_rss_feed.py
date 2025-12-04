import os
import json
import logging
import feedparser
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from email.utils import parsedate_to_datetime

from helpers.types import RSSFeedConfig
from rss.abstract_rss_feed import AbstractRSSFeed

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class LivemintPoliticsRSSFeed(AbstractRSSFeed):
  def get_today_feeds(self) -> List[feedparser.FeedParserDict]:
    today = datetime.now().date()
    today_entries = []
    
    for entry in self.feed.entries:
      published_datetime = parsedate_to_datetime(entry.published)
      published_date = published_datetime.date()
      if published_date == today:
        today_entries.append(entry)
    
    return today_entries

  def parse_feed(self, feed_entries: Optional[List[feedparser.FeedParserDict]] = None) -> List[dict]:
    if feed_entries is None:
      return []
    
    return [
      {
        'title': entry.title,
        'link': entry.link,
        'published': entry.published,
        'summary': entry.summary
      }
      for entry in feed_entries
    ]

if __name__ == '__main__':
  config = RSSFeedConfig(url=os.getenv('LIVEMINT_POLITICS_RSS_FEED'))
  rss_feed = LivemintPoliticsRSSFeed(config=config)
  feed_entries = rss_feed.get_today_feeds()
  parsed_feed_entries = rss_feed.parse_feed(feed_entries)
  logger.info(json.dumps(parsed_feed_entries, indent=2, default=str))



