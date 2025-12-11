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
  llm_prompt += "CHAIN-OF-THOUGHT ANALYSIS\n"
  llm_prompt += "=" * 80 + "\n\n"
  
  llm_prompt += "For each news item, think through these steps:\n\n"
  llm_prompt += "STEP 1: What is the DIRECT impact?\n"
  llm_prompt += "STEP 2: What is the INDIRECT/SECOND-ORDER impact that others might miss?\n"
  llm_prompt += "STEP 3: Is this already priced in? (If news is old or obvious, skip)\n"
  llm_prompt += "STEP 4: What specific asset benefits or loses?\n"
  llm_prompt += "STEP 5: What is my EDGE - the insight the market hasn't realized yet?\n\n"
  
  llm_prompt += "ONLY CREATE A SIGNAL IF:\n"
  llm_prompt += "- You identified a genuine second-order effect\n"
  llm_prompt += "- The insight is non-obvious (retail investors wouldn't think of it)\n"
  llm_prompt += "- You can name a SPECIFIC tradeable asset\n"
  llm_prompt += "- Return empty array [] if no strong signals exist\n\n"
  
  total_news_count = len(political_news_list) + len(market_news_list)
  
  if total_news_count == 0:
    max_recommendations = 0
  elif total_news_count == 1:
    max_recommendations = 2
  elif total_news_count <= 3:
    max_recommendations = 3
  else:
    max_recommendations = 4
  
  if total_news_count > 0:
    llm_prompt += f"Maximum {max_recommendations} signals. Quality over quantity.\n\n"
  
  llm_prompt += "OUTPUT FORMAT (JSON array only):\n\n"
  llm_prompt += "[\n"
  llm_prompt += "  {\n"
  llm_prompt += '    "news_summary_referenced": "<the news>",\n'
  llm_prompt += '    "news_link": "<URL>",\n'
  llm_prompt += '    "news_published": "<date>",\n'
  llm_prompt += '    "news_summary_segment": "MARKET_NEWS" or "POLITICAL_NEWS",\n'
  llm_prompt += '    "reasoning": "<Step 1-5 thinking process>",\n'
  llm_prompt += '    "trading_idea": "BUY/SELL: <Asset>. EDGE: <Your non-obvious insight>",\n'
  llm_prompt += '    "confidence_on_trading_idea": <1-10>\n'
  llm_prompt += "  }\n"
  llm_prompt += "]\n"

  return llm_prompt
