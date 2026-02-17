# 📊 Financial AI Agent System - Complete Guide

**Version 2.0** | Python 3.10+ | February 2026

---

## 🎯 What This System Does

Automated financial analysis system that:
- ✅ Fetches comprehensive company data from multiple sources
- ✅ Analyzes financial statements and ratios
- ✅ Tracks news and sentiment
- ✅ Generates AI-powered investment recommendations
- ✅ Creates SWOT analysis and price targets

**One command, complete insights.**

---

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install agent-framework requests python-dotenv fastmcp pydantic
```

### 2. Configure API Keys

Create `.env` file:
```bash
# Azure OpenAI (Get from portal.azure.com)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_FAST_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_REASONING_DEPLOYMENT=gpt-4o

# Financial Data (Get from financialmodelingprep.com)
FMP_API_KEY=your-fmp-key

# Optional: Alpha Vantage fallback
ALPHA_VANTAGE_API_KEY=your-av-key
```

**Free API Keys:**
- FMP: 300 calls/day free tier
- Alpha Vantage: 25 calls/day free tier

### 3. Run Analysis
```bash
python magentic_agent_enhanced.py
# Enter ticker: AAPL
# Wait 1-2 minutes
# Get complete analysis!
```

---

## 📁 System Architecture

### Core Files (14 files)

**Main System (5 files)**
```
magentic_agent_enhanced.py    # Main orchestrator - RUN THIS
tools_enhanced.py              # 24 financial data tools
financial_agents.py            # Specialized AI agents
chat_client_factory.py         # Azure OpenAI client
agent_dependencies.py          # Configuration
```

**Individual Agents (6 files)**
```
init_agent.py                  # Initialize sessions
entity_agent.py                # Company data enrichment
fetch_news.py                  # News fetching
sentiment_agent.py             # Sentiment analysis
inspector_agent.py             # Data validation
orchestrator_decision_agent.py # Workflow decisions
```

**Testing (3 files)**
```
test_azure_connection.py       # Test Azure setup
test_alpha_vantage.py          # Test Alpha Vantage
setup_verification.py          # Verify complete setup
```

### Data Flow

```
User Input (Ticker)
    ↓
[InitAgent] ───────→ Create unique session ID (GUID)
    ↓
[EntityAgent] ─────→ Fetch company profile & fundamentals
    ↓
[NewsAgent] ───────→ Get recent news articles (20)
    ↓
[SentimentAgent] ──→ Analyze news sentiment
    ↓
[FinancialDataAgent] → Extract comprehensive financial data
    ├→ Income Statements
    ├→ Balance Sheets
    ├→ Cash Flow Statements
    ├→ Key Metrics & Ratios
    ├→ Historical Prices
    ├→ Analyst Estimates
    ├→ Insider Trading
    ├→ Institutional Holdings
    └→ SEC Filings
    ↓
[FinancialAnalysisAgent] → Generate investment analysis
    ├→ Valuation Assessment
    ├→ Financial Health Rating
    ├→ Growth Metrics
    └→ SWOT Analysis
    ↓
[InspectorAgent] ──→ Validate data quality
    ↓
Final Report (JSON)
```

---

## 🛠️ Available Tools (24 Total)

### Primary: FMP API (13 tools)

```python
fmp_get_profile(symbol)              # Company profile & fundamentals
fmp_quote(symbol)                    # Real-time quote
fmp_get_financials(symbol, period)   # Financial statements
fmp_get_key_metrics(symbol)          # Key performance metrics
fmp_get_ratios(symbol)               # Financial ratios
fmp_get_historical_prices(symbol)    # Price history (1 year default)
fmp_stock_news(symbol, limit)        # Recent news articles
fmp_get_analyst_estimates(symbol)    # Analyst forecasts
fmp_get_insider_trading(symbol)      # Insider transactions
fmp_get_institutional_holders(symbol)# Institutional ownership
fmp_get_sec_filings(symbol)          # SEC filings (10-K, 10-Q, 8-K)
fmp_get_earnings_calendar(symbol)    # Earnings dates
fmp_search_symbol(query)             # Search for tickers
```

### Fallback: Alpha Vantage (11 tools)

```python
av_get_quote(symbol)                 # Real-time quote
av_get_company_overview(symbol)      # Company fundamentals
av_get_income_statement(symbol)      # Income statements
av_get_balance_sheet(symbol)         # Balance sheets
av_get_cash_flow(symbol)             # Cash flow statements
av_get_time_series_daily(symbol)     # Historical prices (20+ years)
av_search_symbol(keywords)           # Symbol search
av_get_earnings(symbol)              # Earnings data
av_healthcheck()                     # Test API connection
```

### Hybrid Tools (2 tools)

```python
hybrid_get_quote(symbol)             # FMP first, AV fallback
hybrid_get_company_info(symbol)      # FMP first, AV fallback
```

**How Hybrid Works:**
1. Try FMP API first (primary)
2. If fails → Try Alpha Vantage (fallback)
3. Return data with source tracking

---

## 🤖 AI Agents

### Standard Model Agents (gpt-4o)
**InitAgent** - Creates unique session IDs
**EntityAgent** - Enriches company data (ticker, ISIN, description)

### Fast Model Agents (gpt-4o-mini)
**NewsAgent** - Fetches articles quickly
**WebScraperAgent** - Simple data extraction

### Reasoning Model Agents (gpt-4o)
**FinancialDataAgent** - Comprehensive data extraction
**FinancialAnalysisAgent** - Investment recommendations
**SentimentAgent** - News sentiment analysis
**InspectorAgent** - Data quality validation
**OrchestratorAgent** - Workflow decisions

---

## 📊 Output Structure

```json
{
  "guid": "unique-session-id",
  "finance": {
    "ticker": "AAPL",
    "description": "Apple Inc.",
    "price": 185.50,
    "currency": "USD",
    "marketCap": 2850000000000,
    "peRatio": 30.5,
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "beta": 1.25,
    "News_Sentiment": "Positive"
  },
  "summary_sentiment": {
    "sentiment": "Positive",
    "summary_bullets": [
      "Strong iPhone sales in Q4 2025",
      "Services revenue growing 15% YoY",
      "Positive analyst outlook for 2026"
    ]
  },
  "financial_data": {
    "data_fetched": [
      "profile", "financials", "ratios", 
      "key_metrics", "historical_prices"
    ],
    "summary": {
      "company_name": "Apple Inc.",
      "current_price": 185.50,
      "market_cap": 2850000000000,
      "pe_ratio": 30.5
    }
  },
  "analysis": {
    "recommendation": "Buy",
    "price_target": 210.00,
    "confidence_level": "High",
    "valuation": {
      "current_pe": 30.5,
      "sector_avg_pe": 25.0,
      "rating": "Fair"
    },
    "financial_health": {
      "debt_to_equity": 1.8,
      "current_ratio": 1.0,
      "rating": "Strong"
    },
    "growth_metrics": {
      "revenue_growth_yoy": 8.5,
      "earnings_growth_yoy": 12.0,
      "rating": "Moderate"
    },
    "swot": {
      "strengths": [
        "Strong brand and ecosystem",
        "High profit margins",
        "Growing services revenue"
      ],
      "weaknesses": [
        "High dependence on iPhone sales",
        "Premium pricing limits market share"
      ],
      "opportunities": [
        "Expansion in India and emerging markets",
        "AI integration in products"
      ],
      "threats": [
        "Increased competition",
        "Regulatory pressures"
      ]
    }
  }
}
```

---

## 💻 Usage Examples

### Example 1: Basic Analysis
```python
import asyncio
from magentic_agent_enhanced import run_enhanced_financial_pipeline

async def main():
    result = await run_enhanced_financial_pipeline(
        user_prompt="Analyze Microsoft",
        fetch_comprehensive_data=True,
        perform_analysis=True
    )
    
    print(f"Recommendation: {result['analysis']['recommendation']}")
    print(f"Price Target: ${result['analysis']['price_target']}")

asyncio.run(main())
```

### Example 2: Command Line (Simplest)
```bash
python magentic_agent_enhanced.py
# Enter: AAPL
# Get: Complete analysis automatically
```

### Example 3: Compare Stocks
```python
tickers = ["AAPL", "MSFT", "GOOGL"]

for ticker in tickers:
    result = await run_enhanced_financial_pipeline(ticker)
    print(f"{ticker}: {result['analysis']['recommendation']}")
```

---

## ⚙️ Configuration

### Azure OpenAI Models
**Use GPT 4 models due to low pricing**
**Recommended Setup (Best Balance):**
```bash
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o      # Standard tasks
AZURE_OPENAI_FAST_DEPLOYMENT=gpt-4o-mini      # Quick operations
AZURE_OPENAI_REASONING_DEPLOYMENT=gpt-4o      # Complex analysis
```

**Budget Setup (Most Economical):**
```bash
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_FAST_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_REASONING_DEPLOYMENT=gpt-4o-mini
```

**Premium Setup (Best Quality):**
```bash
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_FAST_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_REASONING_DEPLOYMENT=o1-preview  # Advanced reasoning
```



### Storage Directories

```bash
FINANCE_STATE_DIR=agent_state        # Finance objects
FINANCE_ARTICLES_DIR=agent_articles  # News articles
FINANCIAL_DATA_DIR=financial_data    # Financial data cache
```

Auto-created on first run.

---

## 🔧 Setup & Verification

### Verify Installation
```bash
python setup_verification.py
```

Checks:
- ✅ Python version (3.10+ required)
- ✅ All required files present
- ✅ Dependencies installed
- ✅ Environment configured
- ✅ API keys valid

### Test Azure Connection
```bash
python test_azure_connection.py
```

### Test Alpha Vantage
```bash
python test_alpha_vantage.py
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: 401 Authentication Error**
```
Fix:
1. Check AZURE_OPENAI_ENDPOINT ends with /
2. Verify API key is correct
3. Check deployment names match Azure
```

**Issue: FMP_API_KEY not set**
```
Fix:
1. Create .env file: cp .env.example .env
2. Add your FMP API key
3. Restart Python
```

**Issue: JSON Parse Error**
```
Fix: System now handles this gracefully
- Continues execution
- You still get data
- Analysis may be skipped
```

**Issue: Module not found**
```
Fix:
pip install agent-framework requests python-dotenv fastmcp pydantic
```

**Issue: Rate limit exceeded**
```
Fix:
- FMP free tier: 300 calls/day
- Alpha Vantage free: 25 calls/day
- Wait or upgrade to paid tier
```

---

## 📈 What's New in v2.0

### ✨ New Features

1. **Alpha Vantage Integration**
   - 11 new Alpha Vantage tools
   - Automatic fallback when FMP fails
   - 2 hybrid tools for reliability

2. **Simplified Interface**
   - No more confusing menus
   - Just enter ticker → get analysis
   - One-command operation

3. **Enhanced Error Handling**
   - Graceful JSON error recovery
   - Auto-fix common AI mistakes
   - Better debug output

4. **Improved Type Safety**
   - Full type hints (Python 3.10+)
   - mypy & pyright compatible
   - Pydantic validation

5. **Better Documentation**
   - Unified comprehensive guide
   - Clear examples
   - Troubleshooting section

### 🔄 Changes from v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Data Sources | FMP only | FMP + Alpha Vantage |
| Tools | 13 tools | 24 tools |
| Reliability | Single source | Automatic fallback |
| Interface | 3 menu options | Direct entry |
| Error Handling | Basic | Advanced with auto-fix |
| Documentation | 11 separate files | 1 unified guide |

---

## 💡 Best Practices

### 1. API Key Management
- ✅ Never commit .env to git
- ✅ Use different keys for dev/prod
- ✅ Rotate keys periodically

### 2. Cost Optimization
- ✅ Use gpt-4o-mini for simple tasks
- ✅ Cache results when possible
- ✅ Batch requests when analyzing multiple stocks

### 3. Data Quality
- ✅ Verify ticker before analysis
- ✅ Check data freshness
- ✅ Cross-validate from multiple sources

### 4. Error Handling
- ✅ Always wrap in try-except
- ✅ Log errors for debugging
- ✅ Have fallback strategies

### 5. Performance
- ✅ Use async for multiple stocks
- ✅ Store results incrementally
- ✅ Implement caching layer

---

## 📞 Getting Help

### Quick Checks
1. Run `python setup_verification.py`
2. Check `.env` file exists and has all keys
3. Verify Azure deployments are active
4. Test API connections

### Resources
- Azure OpenAI: https://portal.azure.com
- FMP API: https://financialmodelingprep.com/developer/docs/
- Alpha Vantage: https://www.alphavantage.co/documentation/

### Common Commands
```bash
# Full verification
python setup_verification.py

# Test Azure
python test_azure_connection.py

# Test Alpha Vantage
python test_alpha_vantage.py

# Check Python version
python --version

# List installed packages
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 🎓 Advanced Usage

### Custom Workflows
```python
# Skip analysis, just get data
result = await run_enhanced_financial_pipeline(
    "AAPL",
    fetch_comprehensive_data=True,
    perform_analysis=False  # Skip AI recommendation
)
```

### Batch Processing
```python
import asyncio

async def analyze_portfolio(tickers):
    tasks = [
        run_enhanced_financial_pipeline(ticker)
        for ticker in tickers
    ]
    return await asyncio.gather(*tasks)

results = await analyze_portfolio(["AAPL", "MSFT", "GOOGL"])
```

### Custom Agents
```python
# Add your own specialized agent
def build_custom_agent(chat_client):
    return ChatAgent(
        chat_client=chat_client,
        name="CustomAgent",
        instructions="Your custom instructions..."
    )
```

---

## ✅ Production Checklist

Before deploying to production:

- [ ] All API keys configured
- [ ] Azure OpenAI models deployed
- [ ] Setup verification passes
- [ ] Connection tests successful
- [ ] Error handling tested
- [ ] Logging configured
- [ ] Rate limits understood
- [ ] Backup data sources configured
- [ ] Cost monitoring set up
- [ ] Documentation reviewed

---

## 📊 System Requirements

**Python:** 3.10 or higher (3.11+ recommended)

**Dependencies:**
- agent-framework
- requests
- python-dotenv
- fastmcp
- pydantic

**APIs:**
- Azure OpenAI (required)
- Financial Modeling Prep (required)
- Alpha Vantage (optional, recommended)

**Storage:** ~100 MB for cache

**Network:** Internet connection required

---

## 🎉 Summary

**Your Financial AI Agent System can:**
- ✅ Analyze any stock with one command
- ✅ Fetch data from multiple sources
- ✅ Generate AI-powered recommendations
- ✅ Create comprehensive SWOT analysis
- ✅ Handle errors gracefully
- ✅ Provide reliable fallback options

**Just run:**
```bash
python magentic_agent_enhanced.py
```

**Enter a ticker, get complete insights in 1-2 minutes!**

---

**Version:** 2.0  
**Last Updated:** February 2026  
**License:** MIT  
**Python:** 3.10+  
**Status:** Production Ready ✅
