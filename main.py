import os
import time
import hashlib
import traceback
import schedule
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict
from pymongo.collection import Collection
from openai import OpenAI
from dotenv import load_dotenv

from helpers.types import (
  GrowwConfig,
  RSSFeedConfig,
  ResultantLLMInputPayload,
  PortfolioHolding,
  RSSFeedEntry,
  DatabaseConfig
)
from helpers.generate_groww_access_token import generate_groww_access_token
from helpers.common import filter_unprocessed_feeds
from portfolio.groww_portfolio import GrowwPortfolio
from rss.livemint_politics_rss_feed import LivemintPoliticsRSSFeed
from rss.livemint_market_rss_feed import LivemintMarketRSSFeed
from prompts.news_based_prompt import generate_news_based_prompt
from database.mongo_database import MongoDatabase
from database.models.database_models import FeedType, LLMRequestResponseModel

load_dotenv()

def calculate_pnl(current_price: float, average_price: float, quantity: float) -> Tuple[float, float]:
  pnl = (current_price - average_price) * quantity
  pnl_percentage = ((current_price - average_price) / average_price) * 100 if average_price > 0 else 0
  return pnl, pnl_percentage

def get_portfolio_holdings(
  groww_portfolio: GrowwPortfolio,
  instruments_information: pd.DataFrame,
  groww_holdings: Dict[str, Any]
) -> List[PortfolioHolding]:
  holdings: List[PortfolioHolding] = []
  
  for holding in groww_holdings.get('holdings', []):
    try:
      trading_symbol: str = holding['trading_symbol']
      current_quote: Optional[Dict[str, Any]] = groww_portfolio.get_current_quote(trading_symbol=trading_symbol)
      
      instrument_match = instruments_information[
        instruments_information['trading_symbol'] == trading_symbol
      ]
      
      if instrument_match.empty:
        print(f"Warning: Instrument {trading_symbol} not found in instruments data. Skipping.")
        continue
      
      instrument_name: str = instrument_match['name'].iloc[0]
      quantity: float = holding['quantity']
      average_price: float = holding['average_price']
      current_price: float = current_quote.get('last_price', 0) if current_quote else 0
      
      pnl, pnl_percentage = calculate_pnl(current_price, average_price, quantity)
      
      holdings.append({
        'instrument_name': instrument_name,
        'quantity': quantity,
        'average_price': average_price,
        'current_price': current_price,
        'pnl': pnl,
        'pnl_percentage': pnl_percentage
      })
    except Exception as e:
      print(f"Error processing holding {holding.get('trading_symbol', 'unknown')}: {str(e)}")
      continue
  
  return holdings

def mark_feeds_as_processed(
  feeds: List[RSSFeedEntry],
  feed_table_handle: Collection
) -> None:
  if not feeds:
    return
  
  title_hashes = [
    hashlib.sha256(feed['title'].encode()).hexdigest()
    for feed in feeds
  ]
  
  feed_table_handle.update_many(
    {'title_hash': {'$in': title_hashes}},
    {'$set': {'processed': True}}
  )

def save_llm_request_response(
  prompt: str,
  response: str,
  llm_request_response_handle: Collection,
  mongodb_database: MongoDatabase
) -> None:
  llm_model = LLMRequestResponseModel(
    prompt=prompt,
    prompt_response=response
  )
  llm_dict = asdict(llm_model)
  mongodb_database.save_record(llm_request_response_handle, llm_dict)

def main() -> None:
  database_config = DatabaseConfig(
    url=os.getenv('MONGODB_URI'),
    name=os.getenv('MONGODB_NAME')
  )
  
  mongodb_database = MongoDatabase(config=database_config)
  feed_table_handle = mongodb_database.get_table_handle('feeds')
  llm_request_response_handle = mongodb_database.get_table_handle('llm_request_responses')
  
  auth_token = generate_groww_access_token(
    totp_token=os.getenv('GROWW_TOTP_TOKEN'),
    totp_secret=os.getenv('GROWW_TOTP_SECRET')
  )
  
  instruments_path = os.path.join(
    os.path.dirname(__file__),
    'master',
    'groww_instruments.csv'
  )
  instruments_information = pd.read_csv(instruments_path, low_memory=False)
  
  groww_config = GrowwConfig(auth_token=auth_token)
  groww_portfolio = GrowwPortfolio(config=groww_config)
  
  try:
    groww_holdings = groww_portfolio.get_holdings()
    holdings_information_for_llm = get_portfolio_holdings(
      groww_portfolio,
      instruments_information,
      groww_holdings
    )
  except Exception as e:
    print(f"Error fetching portfolio holdings: {str(e)}")
    print("Continuing with empty portfolio holdings...")
    holdings_information_for_llm = []
  
  politics_config = RSSFeedConfig(url=os.getenv('LIVEMINT_POLITICS_RSS_FEED'))
  politics_feed = LivemintPoliticsRSSFeed(config=politics_config)
  political_news = politics_feed.get_today_feeds()
  parsed_political_news = politics_feed.parse_feed(political_news)
  filtered_political_news = filter_unprocessed_feeds(
    parsed_political_news,
    FeedType.POLITICAL,
    feed_table_handle,
    mongodb_database
  )
  
  market_config = RSSFeedConfig(url=os.getenv('LIVEMINT_MARKET_RSS_FEED'))
  market_feed = LivemintMarketRSSFeed(config=market_config)
  market_news = market_feed.get_today_feeds()
  parsed_market_news = market_feed.parse_feed(market_news)
  filtered_market_news = filter_unprocessed_feeds(
    parsed_market_news,
    FeedType.MARKET,
    feed_table_handle,
    mongodb_database
  )

  all_new_feeds = filtered_political_news + filtered_market_news
  
  if not all_new_feeds:
    print("No new feeds to process. Skipping LLM call.")
    return
  
  resultant_payload: ResultantLLMInputPayload = {
    'current_portfolio_holdings': holdings_information_for_llm,
    'political_news': filtered_political_news,
    'market_news': filtered_market_news
  }
  
  llm_prompt = generate_news_based_prompt(resultant_payload)
  llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
  
  try:
    llm_response = llm_client.chat.completions.create(
      model='gpt-4.1',
      messages=[
        {
          'role': 'system',
          'content': (
            'You are a professional financial advisor and investment analyst. '
            'Your recommendations must be STRICTLY based on the provided news items. '
            'Each recommendation must have a direct, explicit connection to a specific news item. '
            'Do not create recommendations based on general market knowledge or portfolio analysis alone. '
            'Quality over quantity: Only provide recommendations with strong, actionable connections to the news. '
            'Return ONLY a valid JSON array - no additional text, explanations, or markdown formatting outside the JSON.'
          )
        },
        {
          'role': 'user',
          'content': llm_prompt
        }
      ]
    )
    
    response_text = llm_response.choices[0].message.content or ""
    print(response_text)
    
    mark_feeds_as_processed(all_new_feeds, feed_table_handle)
    save_llm_request_response(
      llm_prompt,
      response_text,
      llm_request_response_handle,
      mongodb_database
    )
    
  except Exception as e:
    print(f"Error calling OpenAI API: {str(e)}")
    print("Make sure you have set OPENAI_API_KEY in your .env file and have access to the model.")
    traceback.print_exc()

if __name__ == '__main__':
  schedule.every(30).minutes.do(main)
  
  print("=" * 80)
  print("Macro Investing Advisor - Scheduled Execution")
  print("=" * 80)
  print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  print("Running every 30 minutes...")
  print("Press Ctrl+C to stop")
  print("=" * 80 + "\n")
  
  main()
  
  try:
    while True:
      schedule.run_pending()
      time.sleep(60)
  except KeyboardInterrupt:
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stopping scheduler...")
    print("Goodbye!")


