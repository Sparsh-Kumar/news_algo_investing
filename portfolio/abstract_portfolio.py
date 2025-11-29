from abc import ABC, abstractmethod

# TODO : In future we can add more methods to the portfolio class to add and remove assets, etc.

class AbstractPortfolio(ABC):
  @abstractmethod
  def get_holdings(self):
    pass

  @abstractmethod
  def get_current_quote(self, trading_symbol: str, exchange: str = None, segment: str = None):
    pass


