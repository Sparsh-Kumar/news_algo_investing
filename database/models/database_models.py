from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FeedType(Enum):
  POLITICAL = 'POLITICAL'
  MARKET = 'MARKET'

@dataclass
class FeedModel:
  title: str
  link: str
  summary: str
  type: FeedType
  title_hash: str
  processed: bool
  published_at: datetime


@dataclass
class LLMRequestResponseModel:
  prompt: str
  prompt_response: str

