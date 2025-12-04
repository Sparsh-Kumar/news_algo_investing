from dataclasses import dataclass
from typing import TypedDict, List

@dataclass
class GrowwConfig:
  auth_token: str


@dataclass
class RSSFeedConfig:
  url: str


class PortfolioHolding(TypedDict):
  instrument_name: str
  quantity: float
  average_price: float
  current_price: float
  pnl: float
  pnl_percentage: float


class RSSFeedEntry(TypedDict):
  title: str
  link: str
  published: str
  summary: str


class ResultantLLMInputPayload(TypedDict):
  current_portfolio_holdings: List[PortfolioHolding]
  political_news: List[RSSFeedEntry]
  market_news: List[RSSFeedEntry]


class TradingRecommendation(TypedDict):
  news_summary_referenced: str
  news_summary_segment: str  # "MARKET_NEWS" or "POLITICAL_NEWS"
  trading_idea: str
  confidence_on_trading_idea: int  # 1-10

