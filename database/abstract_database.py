from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from helpers.types import DatabaseConfig

class AbstractDatabase(ABC):
  def __init__(self, config: Optional[DatabaseConfig] = None):
    if not config:
      raise ValueError('Database config is required')
    self.config = config

  @abstractmethod
  def get_table_handle(self, table_name: Optional[str] = None) -> Any:
    pass

  @abstractmethod
  def save_record(self, table_handle: Any, record: Dict[str, Any]) -> Any:
    pass

  @abstractmethod
  def get_record_by_id(self, table_handle: Any, record_id: str) -> Optional[Dict[str, Any]]:
    pass

  @abstractmethod
  def save_multiple_records(self, table_handle: Any, records: List[Dict[str, Any]]) -> Any:
    pass

  @abstractmethod
  def delete_record(self, table_handle: Any, record_id: str) -> Any:
    pass

  @abstractmethod
  def update_record(self, table_handle: Any, record_id: str, data: Dict[str, Any]) -> Any:
    pass



