from helpers.types import ResultantLLMInputPayload

def generate_news_based_prompt(llm_input_payload: ResultantLLMInputPayload) -> str:

  llm_prompt: str = ''
  portfolio_information: list[str] = []
  political_news_list: list[str] = []
  market_news_list: list[str] = []

  for holding in llm_input_payload['current_portfolio_holdings']:
    portfolio_sentence: str = (
      f"I have invested in {holding['instrument_name']} which has average price {holding['average_price']}, "
      f"my pnl percentage for this asset is {holding['pnl_percentage']:.2f}%, and quantity is {holding['quantity']}"
    )
    portfolio_information.append(portfolio_sentence)

  for political_news in llm_input_payload['political_news']:
    political_news_list.append(political_news['summary'])

  for market_news in llm_input_payload['market_news']:
    market_news_list.append(market_news['summary'])
  
  if portfolio_information:
    llm_prompt += "PORTFOLIO HOLDINGS:\n\n"
    for i, portfolio_info in enumerate(portfolio_information, 1):
      llm_prompt += f"{i}. {portfolio_info}\n"
    llm_prompt += "\n"

  if political_news_list:
    llm_prompt += "POLITICAL NEWS:\n\n"
    for i, news in enumerate(political_news_list, 1):
      llm_prompt += f"{i}. {news}\n"
    llm_prompt += "\n"

  if market_news_list:
    llm_prompt += "MARKET NEWS:\n\n"
    for i, news in enumerate(market_news_list, 1):
      llm_prompt += f"{i}. {news}\n"
    llm_prompt += "\n"

  llm_prompt += "=" * 80 + "\n"
  llm_prompt += "INVESTMENT ANALYSIS REQUEST\n"
  llm_prompt += "=" * 80 + "\n\n"
  
  llm_prompt += "Based on the above portfolio holdings, market news, and political news, provide actionable trading recommendations.\n\n"
  
  llm_prompt += "CRITICAL REQUIREMENTS:\n"
  llm_prompt += "- Each recommendation MUST be directly and explicitly linked to a specific news item provided above\n"
  llm_prompt += "- The news item must contain actionable information that supports the trading idea\n"
  llm_prompt += "- DO NOT create recommendations based on portfolio analysis, general market trends, or your own knowledge\n"
  llm_prompt += "- DO NOT infer or assume information not explicitly stated in the news\n"
  llm_prompt += "- If a news item does not contain clear, actionable trading signals, DO NOT create a recommendation for it\n"
  llm_prompt += "- Only provide recommendations where the news directly impacts specific assets, sectors, or market conditions\n\n"
  
  llm_prompt += "RECOMMENDATION GUIDELINES:\n"
  llm_prompt += "1. ASSETS TO BUY:\n"
  llm_prompt += "   - Only recommend if news explicitly mentions growth, positive developments, or opportunities for specific assets/sectors\n"
  llm_prompt += "   - Entry price must be realistic and based on current market conditions mentioned in news or portfolio\n"
  llm_prompt += "   - Exit price should reflect reasonable profit targets (typically 10-20% for medium-term, 5-10% for short-term)\n"
  llm_prompt += "   - Rationale must explain HOW the news directly supports the buy decision\n\n"
  
  llm_prompt += "2. ASSETS TO SELL:\n"
  llm_prompt += "   - Only recommend if news explicitly mentions negative impacts, risks, or challenges for specific assets/sectors\n"
  llm_prompt += "   - OR if the asset has significant negative PnL AND news suggests continued headwinds\n"
  llm_prompt += "   - Entry price should be current average price from portfolio\n"
  llm_prompt += "   - Exit price should minimize losses or lock in remaining profits\n"
  llm_prompt += "   - Rationale must explain HOW the news directly supports the sell decision\n\n"
  
  llm_prompt += "OUTPUT FORMAT:\n"
  llm_prompt += "For each recommendation (buy or sell), provide the information in the following JSON format:\n\n"
  llm_prompt += "{\n"
  llm_prompt += "  \"news_summary_referenced\": \"<exact news summary text that supports this recommendation>\",\n"
  llm_prompt += "  \"news_summary_segment\": \"MARKET_NEWS\" or \"POLITICAL_NEWS\",\n"
  llm_prompt += "  \"trading_idea\": \"<detailed trading idea including asset name, entry price, exit price, and rationale>\",\n"
  llm_prompt += "  \"confidence_on_trading_idea\": <number between 1 and 10>\n"
  llm_prompt += "}\n\n"
  
  total_news_count = len(political_news_list) + len(market_news_list)
  
  if total_news_count == 0:
    max_recommendations = 0
  elif total_news_count == 1:
    max_recommendations = 2
  elif total_news_count <= 3:
    max_recommendations = 4
  else:
    max_recommendations = 6
  
  llm_prompt += "QUALITY STANDARDS:\n"
  if total_news_count > 0:
    llm_prompt += f"- Provide ONLY {max_recommendations} recommendations MAXIMUM\n"
    llm_prompt += "- It is BETTER to provide fewer high-quality recommendations than many weak ones\n"
    llm_prompt += "- Each recommendation's 'news_summary_referenced' MUST be the EXACT, COMPLETE text from one of the news items listed above\n"
    llm_prompt += "- The trading_idea must clearly explain the CAUSAL relationship: How does this specific news lead to this trading action?\n"
    llm_prompt += "- Asset names must be specific and tradeable (use exact ETF names, stock symbols, or clearly identifiable instruments)\n"
    llm_prompt += "- Entry and exit prices must be specific numbers, not ranges or vague terms\n"
    llm_prompt += "- Confidence score: Use 7-10 only for recommendations with strong, direct news connection. Use 4-6 for moderate connections. Use 1-3 only if forced to provide a recommendation with weak connection\n"
  else:
    llm_prompt += "- No news items were provided. Skip recommendations or provide only if portfolio analysis strongly suggests action.\n"
  
  llm_prompt += "\nVALIDATION CHECKLIST (each recommendation must pass ALL):\n"
  llm_prompt += "✓ The news_summary_referenced is copied EXACTLY from the news items above\n"
  llm_prompt += "✓ The news explicitly mentions or clearly implies impact on the recommended asset/sector\n"
  llm_prompt += "✓ The trading_idea explains a clear cause-and-effect relationship\n"
  llm_prompt += "✓ Entry and exit prices are specific numbers\n"
  llm_prompt += "✓ The recommendation is actionable and implementable\n\n"
  
  llm_prompt += "OUTPUT FORMAT:\n"
  llm_prompt += "Return ONLY a JSON array of recommendations. No additional text or explanations.\n"
  llm_prompt += "Each recommendation must follow this exact format:\n\n"
  llm_prompt += "[\n"
  llm_prompt += "  {\n"
  llm_prompt += '    "news_summary_referenced": "<EXACT complete text from news items above>",\n'
  llm_prompt += '    "news_summary_segment": "MARKET_NEWS" or "POLITICAL_NEWS",\n'
  llm_prompt += '    "trading_idea": "<BUY/SELL: Asset name at entry price ₹X, exit at ₹Y. Clear explanation of how the news supports this action>",\n'
  llm_prompt += '    "confidence_on_trading_idea": <number 1-10>\n'
  llm_prompt += "  }\n"
  llm_prompt += "]\n\n"
  
  llm_prompt += "Remember: Quality over quantity. Only provide recommendations with strong, direct connections to the provided news.\n"

  return llm_prompt

