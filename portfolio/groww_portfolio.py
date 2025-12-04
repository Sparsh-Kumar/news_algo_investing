from typing import Optional, Dict, Any
from growwapi import GrowwAPI

from helpers.types import GrowwConfig
from portfolio.abstract_portfolio import AbstractPortfolio

class GrowwPortfolio(AbstractPortfolio):
  TIMEOUT = 5

  def __init__(self, config: Optional[GrowwConfig] = None):
    if config is None:
      raise ValueError('GrowwConfig is required')
    self.config = config
    self.groww = GrowwAPI(self.config.auth_token)

  def get_holdings(self) -> Dict[str, Any]:
    return self.groww.get_holdings_for_user(timeout=self.TIMEOUT)

  def get_current_quote(
    self,
    trading_symbol: str,
    exchange: Optional[str] = None,
    segment: Optional[str] = None
  ) -> Optional[Dict[str, Any]]:
    exchange = exchange or self.groww.EXCHANGE_NSE
    segment = segment or self.groww.SEGMENT_CASH
    return self.groww.get_quote(
      trading_symbol=trading_symbol,
      exchange=exchange,
      segment=segment
    )


