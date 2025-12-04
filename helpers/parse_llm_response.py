import json
import re
from typing import List, Dict, Any
from helpers.types import TradingRecommendation

def parse_llm_response(llm_response_text: str) -> Dict[str, List[TradingRecommendation]]:
    """
    Parse LLM response text and extract structured trading recommendations.
    
    Args:
        llm_response_text: The raw text response from the LLM
    
    Returns:
        Dictionary with 'buy_recommendations' and 'sell_recommendations' lists
    """
    buy_recommendations: List[TradingRecommendation] = []
    sell_recommendations: List[TradingRecommendation] = []
    
    # Find all JSON code blocks in the response (handles ```json ... ``` format)
    json_code_block_pattern = r'```json\s*(\{.*?\})\s*```'
    json_matches = re.findall(json_code_block_pattern, llm_response_text, re.DOTALL)
    
    # If no code blocks found, try to find JSON objects directly
    if not json_matches:
        # Pattern to match JSON objects that contain the required fields
        # This handles multi-line JSON objects
        json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*"news_summary_referenced"(?:[^{}]|(?:\{[^{}]*\}))*\}'
        json_matches = re.findall(json_pattern, llm_response_text, re.DOTALL)
    
    # Parse each JSON object
    for json_str in json_matches:
        try:
            # Clean up the JSON string
            json_str = json_str.strip()
            # Remove any trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            recommendation: Dict[str, Any] = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['news_summary_referenced', 'news_summary_segment', 
                             'trading_idea', 'confidence_on_trading_idea']
            if all(key in recommendation for key in required_fields):
                # Determine if it's a buy or sell recommendation
                # Check section headers or trading_idea content
                trading_idea_lower = recommendation['trading_idea'].lower()
                
                # Check context around the JSON (look for BUY/SELL headers)
                json_start_pos = llm_response_text.find(json_str)
                context_before = llm_response_text[max(0, json_start_pos-200):json_start_pos].lower()
                
                is_sell = (
                    'sell' in trading_idea_lower or 
                    'exit' in trading_idea_lower or 
                    'redeploy' in trading_idea_lower or
                    'sell recommendation' in context_before or
                    '### sell' in context_before or
                    '#### sell' in context_before
                )
                
                is_buy = (
                    'buy' in trading_idea_lower or 
                    'purchase' in trading_idea_lower or 
                    'enter' in trading_idea_lower or
                    'buy recommendation' in context_before or
                    '### buy' in context_before or
                    '#### buy' in context_before
                )
                
                if is_sell:
                    sell_recommendations.append(recommendation)
                elif is_buy:
                    buy_recommendations.append(recommendation)
                else:
                    # Default to buy if unclear
                    buy_recommendations.append(recommendation)
                    
        except json.JSONDecodeError:
            # Skip invalid JSON
            continue
        except Exception:
            # Skip any other errors
            continue
    
    return {
        'buy_recommendations': buy_recommendations,
        'sell_recommendations': sell_recommendations,
        'raw_response': llm_response_text
    }

def format_recommendations(parsed_data: Dict[str, List[TradingRecommendation]]) -> str:
    """
    Format parsed recommendations into a readable string.
    
    Args:
        parsed_data: Dictionary with buy_recommendations and sell_recommendations
    
    Returns:
        Formatted string representation
    """
    output: List[str] = []
    
    buy_recs = parsed_data.get('buy_recommendations', [])
    sell_recs = parsed_data.get('sell_recommendations', [])
    
    if buy_recs:
        output.append("=" * 80)
        output.append("BUY RECOMMENDATIONS")
        output.append("=" * 80)
        for i, rec in enumerate(buy_recs, 1):
            output.append(f"\n{i}. {rec['trading_idea']}")
            output.append(f"   News: {rec['news_summary_referenced'][:100]}...")
            output.append(f"   Segment: {rec['news_summary_segment']}")
            output.append(f"   Confidence: {rec['confidence_on_trading_idea']}/10")
    
    if sell_recs:
        output.append("\n" + "=" * 80)
        output.append("SELL RECOMMENDATIONS")
        output.append("=" * 80)
        for i, rec in enumerate(sell_recs, 1):
            output.append(f"\n{i}. {rec['trading_idea']}")
            output.append(f"   News: {rec['news_summary_referenced'][:100]}...")
            output.append(f"   Segment: {rec['news_summary_segment']}")
            output.append(f"   Confidence: {rec['confidence_on_trading_idea']}/10")
    
    return "\n".join(output)

