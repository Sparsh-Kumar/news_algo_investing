import os
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
from helpers.types import GrowwConfig
from helpers.generate_groww_access_token import generate_groww_access_token
from portfolio.groww_portfolio import GrowwPortfolio

load_dotenv()

def main():

  auth_token = generate_groww_access_token(
    totp_token = os.getenv('GROWW_TOTP_TOKEN'),
    totp_secret = os.getenv('GROWW_TOTP_SECRET')
  )

  instruments_information = pd.read_csv(os.path.join(os.path.dirname(__file__), 'master', 'groww_instruments.csv'), low_memory = False)
  groww_config = GrowwConfig(auth_token = auth_token)
  groww_portfolio = GrowwPortfolio(config = groww_config)
  groww_holdings = groww_portfolio.get_holdings()

  holdings_information_for_llm = []

  for holding in groww_holdings['holdings']:
    trading_symbol = holding['trading_symbol']
    current_quote = groww_portfolio.get_current_quote(trading_symbol = trading_symbol)
    instrument_name = instruments_information[instruments_information['trading_symbol'] == trading_symbol]['name'].iloc[0]
    quantity = holding['quantity']
    average_price = holding['average_price']
    current_price = current_quote.get('last_price', 0) if current_quote else 0
    
    pnl = (current_price - average_price) * quantity
    pnl_percentage = ((current_price - average_price) / average_price) * 100 if average_price > 0 else 0
    
    holdings_information_for_llm.append({
      'instrument_name': instrument_name,
      'quantity': quantity,
      'average_price': average_price,
      'current_price': current_price,
      'pnl': pnl,
      'pnl_percentage': pnl_percentage
    })
  
  pprint(holdings_information_for_llm)

if __name__ == '__main__':
  main()
