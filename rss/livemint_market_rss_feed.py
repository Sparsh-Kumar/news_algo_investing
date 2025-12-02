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
  def get_today_feeds(self):

    today_entries = []
    today = datetime.now().date()

    for entry in self.feed.entries:
      published_datetime = parsedate_to_datetime(entry.published)
      published_date = published_datetime.date()
      if published_date == today:
        today_entries.append(entry)

    return today_entries

  def parse_feed(self, feed_entries: List[feedparser.FeedParserDict] | None = None):
    parsed_feed_entries = []
    for entry in feed_entries:
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
  feed_entries = rss_feed.get_today_feeds()
  parsed_feed_entries = rss_feed.parse_feed(feed_entries)
  pprint(parsed_feed_entries)


