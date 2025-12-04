from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any, List, Optional
from datetime import datetime

from helpers.types import DatabaseConfig
from database.abstract_database import AbstractDatabase

class MongoDatabase(AbstractDatabase):
  def __init__(self, config: Optional[DatabaseConfig] = None):
    super().__init__(config)
    db_url = self.config.url or 'mongodb://localhost:27017/'
    db_name = self.config.name or 'news_investing'
    self.client = MongoClient(db_url)
    self.db = self.client[db_name]

  def get_table_handle(self, table_name: Optional[str] = None) -> Collection:
    if not table_name:
      raise ValueError('Table name is required.')
    return self.db[table_name]

  def save_record(self, table_handle: Collection, data: Dict[str, Any]) -> Any:
    now = datetime.utcnow()
    data['created_at'] = now
    data['updated_at'] = now
    return table_handle.insert_one(data)

  def get_record_by_id(self, table_handle: Collection, record_id: str) -> Optional[Dict[str, Any]]:
    return table_handle.find_one({'_id': record_id})

  def save_multiple_records(self, table_handle: Collection, records: List[Dict[str, Any]]) -> Any:
    if not records:
      return None
    
    now = datetime.utcnow()
    for record in records:
      record['created_at'] = now
      record['updated_at'] = now
    return table_handle.insert_many(records)

  def delete_record(self, table_handle: Collection, record_id: str) -> Any:
    return table_handle.delete_one({'_id': record_id})

  def update_record(self, table_handle: Collection, record_id: str, data: Dict[str, Any]) -> Any:
    now = datetime.utcnow()
    data['updated_at'] = now
    return table_handle.update_one(
      {'_id': record_id},
      {
        '$setOnInsert': {'created_at': now},
        '$set': data
      },
      {'upsert': True}
    )


