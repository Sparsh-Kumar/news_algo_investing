from growwapi import GrowwAPI
from helpers.types import GrowwConfig
from portfolio.abstract_portfolio import AbstractPortfolio

class GrowwPortfolio(AbstractPortfolio):
  def __init__(self, config: GrowwConfig | None = None):
    self.timeout = 5
    self.config = config
    self.groww = GrowwAPI(self.config.auth_token)

  def get_holdings(self):
    holdings = self.groww.get_holdings_for_user(timeout = self.timeout)
    return holdings

  def get_current_quote(self, trading_symbol: str, exchange: str = None, segment: str = None):
    exchange = exchange if exchange else self.groww.EXCHANGE_NSE
    segment = segment if segment else self.groww.SEGMENT_CASH
    return self.groww.get_quote(
      trading_symbol = trading_symbol,
      exchange = exchange,
      segment = segment
    )


