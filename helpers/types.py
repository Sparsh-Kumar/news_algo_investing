from dataclasses import dataclass

@dataclass
class GrowwConfig:
  auth_token: str


@dataclass
class RSSFeedConfig:
  url: str

