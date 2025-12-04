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

  # Add instructions for LLM analysis
  llm_prompt += "=" * 80 + "\n"
  llm_prompt += "INVESTMENT ANALYSIS REQUEST\n"
  llm_prompt += "=" * 80 + "\n\n"
  
  llm_prompt += "Based on the above portfolio holdings, market news, and political news, please provide the following analysis:\n\n"
  
  llm_prompt += "1. INVESTING OPPORTUNITIES:\n"
  llm_prompt += "   Identify good investing opportunities that align with:\n"
  llm_prompt += "   - Your current portfolio composition and performance\n"
  llm_prompt += "   - Market trends and news\n"
  llm_prompt += "   - Political developments that may impact markets\n"
  llm_prompt += "   - Risk diversification opportunities\n\n"
  
  llm_prompt += "2. ASSETS TO BUY:\n"
  llm_prompt += "   Recommend specific assets to purchase with:\n"
  llm_prompt += "   - Exact entry price (target buy price)\n"
  llm_prompt += "   - Exit price (target sell price for profit taking)\n"
  llm_prompt += "   - Rationale based on portfolio analysis and news\n"
  llm_prompt += "   - Consider portfolio diversification and risk management\n\n"
  
  llm_prompt += "3. ASSETS TO SELL:\n"
  llm_prompt += "   Recommend specific assets from your current portfolio to sell with:\n"
  llm_prompt += "   - Exact entry price (current or average price)\n"
  llm_prompt += "   - Exit price (target sell price)\n"
  llm_prompt += "   - Rationale based on portfolio performance, news impact, or risk management\n"
  llm_prompt += "   - Consider cutting losses or taking profits strategically\n\n"
  
  llm_prompt += "OUTPUT FORMAT:\n"
  llm_prompt += "For each recommendation (buy or sell), provide the information in the following JSON format:\n\n"
  llm_prompt += "{\n"
  llm_prompt += "  \"news_summary_referenced\": \"<exact news summary text that supports this recommendation>\",\n"
  llm_prompt += "  \"news_summary_segment\": \"MARKET_NEWS\" or \"POLITICAL_NEWS\",\n"
  llm_prompt += "  \"trading_idea\": \"<detailed trading idea including asset name, entry price, exit price, and rationale>\",\n"
  llm_prompt += "  \"confidence_on_trading_idea\": <number between 1 and 10>\n"
  llm_prompt += "}\n\n"
  
  llm_prompt += "IMPORTANT INSTRUCTIONS:\n"
  llm_prompt += "- Provide multiple recommendations (at least 2-3 buy opportunities and 1-2 sell recommendations if applicable)\n"
  llm_prompt += "- Each recommendation must reference specific news items from the provided market or political news\n"
  llm_prompt += "- Confidence score should reflect: 1-3 (low confidence), 4-6 (moderate), 7-8 (high), 9-10 (very high)\n"
  llm_prompt += "- Consider portfolio diversification - avoid over-concentration in similar sectors\n"
  llm_prompt += "- Entry and exit prices should be realistic and based on current market conditions\n"
  llm_prompt += "- For sell recommendations, prioritize assets with negative PnL or those that may be impacted by news\n"
  llm_prompt += "- For buy recommendations, consider assets that complement your existing portfolio\n"
  llm_prompt += "- Always provide clear rationale connecting the news to your trading idea\n\n"
  
  llm_prompt += "Please provide your analysis now:\n"

  return llm_prompt

