# News Investing Advisor

An automated investment advisor that analyzes market and political news to provide AI-powered trading recommendations based on your portfolio holdings.

## Overview

The system continuously monitors RSS feeds from Livemint (market and political news), analyzes them alongside your Groww portfolio, and generates actionable trading recommendations using OpenAI's GPT-4 model. All recommendations are strictly tied to specific news items, ensuring data-driven decision making.

## Features

- **Portfolio Integration**: Automatically fetches and analyzes your Groww portfolio holdings
- **News Monitoring**: Tracks market and political news from Livemint RSS feeds
- **AI Analysis**: Uses GPT-4 to generate trading recommendations with confidence scores
- **Duplicate Prevention**: Tracks processed news items to avoid redundant analysis
- **Scheduled Execution**: Runs automatically every 30 minutes
- **Data Persistence**: Stores all feeds and LLM responses in MongoDB
- **Web Dashboard**: Interactive dashboard to view LLM responses and recommendations
- **REST API**: API server to access today's recommendations programmatically

## Prerequisites

- Python 3.12+
- MongoDB instance
- Groww account with TOTP authentication
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd NewsInvestingAdvisor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_NAME=your_database_name
GROWW_TOTP_TOKEN=your_groww_totp_token
GROWW_TOTP_SECRET=your_groww_totp_secret
OPENAI_API_KEY=your_openai_api_key
LIVEMINT_POLITICS_RSS_FEED=https://www.livemint.com/rss/politics
LIVEMINT_MARKET_RSS_FEED=https://www.livemint.com/rss/markets
```

## Usage

### Running the News Advisor

Run the advisor:
```bash
python main.py
```

Or use the provided script:
```bash
./scripts/start_news_advisor.sh
```

The system will:
1. Fetch your portfolio holdings from Groww
2. Retrieve today's news from configured RSS feeds
3. Filter out previously processed news items
4. Generate AI-powered trading recommendations
5. Log recommendations and save them to MongoDB
6. Repeat every 30 minutes

Press `Ctrl+C` to stop the scheduler.

### Running the API Server and Dashboard

Start the API server:
```bash
python api.py
```

Or use the provided script:
```bash
./scripts/start_api.sh
```

The server will start on `http://localhost:5000` by default. Access the dashboard at:
- **Dashboard**: `http://localhost:5000/`
- **API Endpoint**: `http://localhost:5000/api/llm-responses/today`

**Configuration** (optional environment variables):
- `FLASK_DEBUG=true` - Enable debug mode (default: false)
- `FLASK_HOST=0.0.0.0` - Server host (default: 0.0.0.0)
- `FLASK_PORT=5000` - Server port (default: 5000)

**Dashboard Features**:
- View today's LLM request/response records
- Auto-refresh every 30 seconds
- Manual refresh option
- Responsive design for mobile and desktop

## Project Structure

```
NewsInvestingAdvisor/
├── main.py                 # Main execution script
├── api.py                  # Flask API server
├── dashboard/              # Web dashboard (HTML, CSS, JS)
├── database/               # MongoDB integration
├── portfolio/              # Groww portfolio integration
├── rss/                    # RSS feed parsers
├── prompts/                # LLM prompt generation
├── helpers/                # Utility functions
├── master/                 # Instrument master data
└── scripts/                # Startup scripts
```

## How It Works

1. **Portfolio Analysis**: Fetches current holdings, calculates P&L, and prepares portfolio context
2. **News Aggregation**: Collects today's market and political news from RSS feeds
3. **Deduplication**: Filters out news items that have already been processed
4. **AI Processing**: Sends portfolio and news data to GPT-4 for analysis
5. **Recommendation Generation**: Receives structured JSON recommendations with:
   - Referenced news item
   - Trading idea (buy/sell with entry/exit prices)
   - Confidence score (1-10)
6. **Data Storage**: Saves all feeds and recommendations to MongoDB

## Output Format

Recommendations are returned as JSON arrays:
```json
[
  {
    "news_summary_referenced": "Exact news text...",
    "news_summary_segment": "MARKET_NEWS",
    "trading_idea": "BUY: Asset name at entry price ₹X, exit at ₹Y. Rationale...",
    "confidence_on_trading_idea": 8
  }
]
```

## Dependencies

- `openai` - GPT-4 API integration
- `growwapi` - Groww portfolio access
- `feedparser` - RSS feed parsing
- `pymongo` - MongoDB operations
- `pandas` - Data manipulation
- `schedule` - Task scheduling
- `pyotp` - TOTP authentication
- `flask` - Web framework for API server
- `flask-cors` - CORS support for API

## Notes

- The system only processes news from the current day
- Recommendations are strictly tied to provided news items
- All processed feeds are marked to prevent duplicate analysis
- Portfolio fetching errors are handled gracefully (continues with empty portfolio)

