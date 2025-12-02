import os
import feedparser
from datetime import datetime
from pprint import pprint
from typing import List
from dotenv import load_dotenv
from helpers.types import RSSFeedConfig
from email.utils import parsedate_to_datetime
from rss.abstract_rss_feed import AbstractRSSFeed

load_dotenv()

class LivemintMarketRSSFeed(AbstractRSSFeed):
  def get_feed(self):
    return self.feed.entries

  def parse_feed(self, feed_entries: List[feedparser.FeedParserDict] | None = None):
    today = datetime.now().date()
    parsed_feed_entries = []
    for entry in feed_entries:
      published_datetime = parsedate_to_datetime(entry.published)
      published_date = published_datetime.date()
      if published_date == today:
        parsed_feed_entries.append({
          'title': entry.title,
          'link': entry.link,
          'published': entry.published,
          'summary': entry.summary
        })
    return parsed_feed_entries

if __name__ == '__main__':
  config = RSSFeedConfig(url = os.getenv('LIVEMINT_MARKET_RSS_FEED'))
  rss_feed = LivemintMarketRSSFeed(config = config)
  feed_entries = rss_feed.get_feed()
  parsed_feed_entries = rss_feed.parse_feed(feed_entries)
  pprint(parsed_feed_entries)


