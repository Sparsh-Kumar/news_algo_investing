import os
import feedparser
import pandas as pd
from typing import List, Dict, Any, Optional
from pprint import pprint
from openai import OpenAI
from dotenv import load_dotenv
from helpers.types import GrowwConfig, RSSFeedConfig, ResultantLLMInputPayload, PortfolioHolding, RSSFeedEntry
from helpers.generate_groww_access_token import generate_groww_access_token
from helpers.parse_llm_response import parse_llm_response, format_recommendations
from portfolio.groww_portfolio import GrowwPortfolio
from rss.livemint_politics_rss_feed import LivemintPoliticsRSSFeed
from rss.livemint_market_rss_feed import LivemintMarketRSSFeed
from prompts.news_based_prompt import generate_news_based_prompt

load_dotenv()

def main() -> None:

  # Get portfolio holdings

  auth_token: str = generate_groww_access_token(
    totp_token = os.getenv('GROWW_TOTP_TOKEN'),
    totp_secret = os.getenv('GROWW_TOTP_SECRET')
  )
  
  instruments_information: pd.DataFrame = pd.read_csv(os.path.join(os.path.dirname(__file__), 'master', 'groww_instruments.csv'), low_memory = False)
  groww_config: GrowwConfig = GrowwConfig(auth_token = auth_token)
  groww_portfolio: GrowwPortfolio = GrowwPortfolio(config = groww_config)
  groww_holdings: Dict[str, Any] = groww_portfolio.get_holdings()

  holdings_information_for_llm: List[PortfolioHolding] = []

  for holding in groww_holdings['holdings']:
    holding_dict: Dict[str, Any] = holding
    trading_symbol: str = holding_dict['trading_symbol']
    current_quote: Optional[Dict[str, Any]] = groww_portfolio.get_current_quote(trading_symbol = trading_symbol)
    instrument_name: str = instruments_information[instruments_information['trading_symbol'] == trading_symbol]['name'].iloc[0]
    quantity: float = holding_dict['quantity']
    average_price: float = holding_dict['average_price']
    current_price: float = current_quote.get('last_price', 0) if current_quote else 0

    pnl: float = (current_price - average_price) * quantity
    pnl_percentage: float = ((current_price - average_price) / average_price) * 100 if average_price > 0 else 0

    holdings_information_for_llm.append({
      'instrument_name': instrument_name,
      'quantity': quantity,
      'average_price': average_price,
      'current_price': current_price,
      'pnl': pnl,
      'pnl_percentage': pnl_percentage
    })
  
  # Get political news

  livemint_politics_rss_feed_config: RSSFeedConfig = RSSFeedConfig(
    url = os.getenv('LIVEMINT_POLITICS_RSS_FEED')
  )
  livemint_politics_rss_feed: LivemintPoliticsRSSFeed = LivemintPoliticsRSSFeed(config = livemint_politics_rss_feed_config)
  political_news_feed: List[feedparser.FeedParserDict] = livemint_politics_rss_feed.get_today_feeds()
  parsed_political_news_feed: List[RSSFeedEntry] = livemint_politics_rss_feed.parse_feed(political_news_feed)

  # Get market news

  livemint_market_rss_feed_config: RSSFeedConfig = RSSFeedConfig(
    url = os.getenv('LIVEMINT_MARKET_RSS_FEED')
  )
  livemint_market_rss_feed: LivemintMarketRSSFeed = LivemintMarketRSSFeed(config = livemint_market_rss_feed_config)
  market_news_feed: List[feedparser.FeedParserDict] = livemint_market_rss_feed.get_today_feeds()
  parsed_market_news_feed: List[RSSFeedEntry] = livemint_market_rss_feed.parse_feed(market_news_feed)

  resultant_payload: ResultantLLMInputPayload = {
    'current_portfolio_holdings': holdings_information_for_llm,
    'political_news': parsed_political_news_feed,
    'market_news': parsed_market_news_feed
  }

  llm_prompt: str = generate_news_based_prompt(resultant_payload)
  llm_client = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
  )

  try:
    llm_response = llm_client.chat.completions.create(
      model = 'gpt-4.1',
      messages = [
        {
          'role': 'system',
          'content': 'You are a professional financial advisor and investment analyst. Provide detailed, well-reasoned investment recommendations based on portfolio data and market news. Always format your recommendations as JSON objects within markdown code blocks.'
        },
        {
          'role': 'user',
          'content': llm_prompt
        }
      ]
    )
    response_text: str = llm_response.choices[0].message.content or ""
    print(response_text)
  except Exception as e:
    print(f"Error calling OpenAI API: {str(e)}")
    print("Make sure you have set OPENAI_API_KEY in your .env file and have access to the model.")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
  main()


