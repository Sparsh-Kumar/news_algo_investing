from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AbstractPortfolio(ABC):
  @abstractmethod
  def get_holdings(self) -> Dict[str, Any]:
    pass

  @abstractmethod
  def get_current_quote(
    self,
    trading_symbol: str,
    exchange: Optional[str] = None,
    segment: Optional[str] = None
  ) -> Optional[Dict[str, Any]]:
    pass


