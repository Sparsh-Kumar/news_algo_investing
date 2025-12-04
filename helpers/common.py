import hashlib
from typing import List, Dict, Any
from dataclasses import asdict
from email.utils import parsedate_to_datetime
from pymongo.collection import Collection

from database.models.database_models import FeedModel, FeedType
from database.mongo_database import MongoDatabase
from helpers.types import RSSFeedEntry

def _calculate_title_hash(title: str) -> str:
  return hashlib.sha256(title.encode()).hexdigest()

def _create_feed_model(feed: RSSFeedEntry, feed_type: FeedType, title_hash: str) -> FeedModel:
  published_datetime = parsedate_to_datetime(feed['published'])
  return FeedModel(
    title=feed['title'],
    link=feed['link'],
    summary=feed['summary'],
    type=feed_type,
    title_hash=title_hash,
    processed=False,
    published_at=published_datetime,
  )

def filter_unprocessed_feeds(
  parsed_feeds: List[RSSFeedEntry],
  feed_type: FeedType,
  feed_table_handle: Collection,
  mongodb_database: MongoDatabase
) -> List[RSSFeedEntry]:
  if not parsed_feeds:
    return []
  
  title_hashes = [_calculate_title_hash(feed['title']) for feed in parsed_feeds]
  existing_feeds = feed_table_handle.find({'title_hash': {'$in': title_hashes}})
  existing_hashes = {doc['title_hash'] for doc in existing_feeds}
  
  new_feeds: List[RSSFeedEntry] = []
  feed_dicts: List[Dict[str, Any]] = []
  
  for feed in parsed_feeds:
    title_hash = _calculate_title_hash(feed['title'])
    if title_hash not in existing_hashes:
      feed_model = _create_feed_model(feed, feed_type, title_hash)
      feed_dict = asdict(feed_model)
      feed_dict['type'] = feed_dict['type'].value
      feed_dicts.append(feed_dict)
      new_feeds.append(feed)

  if feed_dicts:
    mongodb_database.save_multiple_records(feed_table_handle, feed_dicts)

  return new_feeds

