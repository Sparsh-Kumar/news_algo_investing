from helpers.types import ResultantLLMInputPayload

def generate_news_based_prompt(llm_input_payload: ResultantLLMInputPayload) -> str:

  llm_prompt: str = ''
  portfolio_information: list[str] = []
  political_news_list: list[dict] = []
  market_news_list: list[dict] = []

  for holding in llm_input_payload['current_portfolio_holdings']:
    portfolio_sentence: str = (
      f"I have invested in {holding['instrument_name']} which has average price {holding['average_price']}, "
      f"my pnl percentage for this asset is {holding['pnl_percentage']:.2f}%, and quantity is {holding['quantity']}"
    )
    portfolio_information.append(portfolio_sentence)

  for news in llm_input_payload['political_news']:
    political_news_list.append({
      'summary': news['summary'],
      'link': news.get('link', ''),
      'published': news.get('published', '')
    })

  for news in llm_input_payload['market_news']:
    market_news_list.append({
      'summary': news['summary'],
      'link': news.get('link', ''),
      'published': news.get('published', '')
    })
  
  if portfolio_information:
    llm_prompt += "PORTFOLIO HOLDINGS:\n\n"
    for i, portfolio_info in enumerate(portfolio_information, 1):
      llm_prompt += f"{i}. {portfolio_info}\n"
    llm_prompt += "\n"

  if political_news_list:
    llm_prompt += "POLITICAL NEWS:\n\n"
    for i, news in enumerate(political_news_list, 1):
      llm_prompt += f"{i}. {news['summary']}\n"
      llm_prompt += f"   Link: {news['link']}\n"
      llm_prompt += f"   Published: {news['published']}\n\n"

  if market_news_list:
    llm_prompt += "MARKET NEWS:\n\n"
    for i, news in enumerate(market_news_list, 1):
      llm_prompt += f"{i}. {news['summary']}\n"
      llm_prompt += f"   Link: {news['link']}\n"
      llm_prompt += f"   Published: {news['published']}\n\n"

  llm_prompt += "=" * 80 + "\n"
  llm_prompt += "TRADING SIGNAL ANALYSIS\n"
  llm_prompt += "=" * 80 + "\n\n"
  
  llm_prompt += "Analyze the news above and provide trading signals with clear EDGE explanations.\n\n"
  
  llm_prompt += "FOR EACH SIGNAL, PROVIDE:\n"
  llm_prompt += "1. ACTION: What to BUY or SELL (specific asset/stock name)\n"
  llm_prompt += "2. EDGE: The non-obvious insight - what is the market missing?\n"
  llm_prompt += "3. NEWS: Include the summary, link, and published date\n\n"
  
  total_news_count = len(political_news_list) + len(market_news_list)
  
  if total_news_count == 0:
    max_recommendations = 0
  elif total_news_count == 1:
    max_recommendations = 2
  elif total_news_count <= 3:
    max_recommendations = 4
  else:
    max_recommendations = 6
  
  if total_news_count > 0:
    llm_prompt += f"Provide up to {max_recommendations} high-quality signals.\n\n"
  
  llm_prompt += "OUTPUT FORMAT (JSON array only, no other text):\n\n"
  llm_prompt += "[\n"
  llm_prompt += "  {\n"
  llm_prompt += '    "news_summary_referenced": "<the news summary>",\n'
  llm_prompt += '    "news_link": "<the news link URL>",\n'
  llm_prompt += '    "news_published": "<the published date>",\n'
  llm_prompt += '    "news_summary_segment": "MARKET_NEWS" or "POLITICAL_NEWS",\n'
  llm_prompt += '    "trading_idea": "BUY/SELL: <Asset Name>. EDGE: <Your insight>",\n'
  llm_prompt += '    "confidence_on_trading_idea": <1-10>\n'
  llm_prompt += "  }\n"
  llm_prompt += "]\n"

  return llm_prompt
