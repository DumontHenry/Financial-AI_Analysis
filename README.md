# 🤖 Financial AI Agent System

> **Conversational AI financial advisor** — talk to it naturally, get institutional-grade analysis on any stock, ETF, or index worldwide.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-0078D4) ![FMP](https://img.shields.io/badge/Data-FMP%20%2B%20Web-green) ![Teams](https://img.shields.io/badge/Deploy-Microsoft%20Teams-purple) ![Version](https://img.shields.io/badge/Version-3.0-orange)

---

## ✨ What Makes This Different

Unlike tools that require exact ticker symbols, this agent **finds any company dynamically**:

```
You: Analyze Volkswagen
→ 🔍 Searching for 'volkswagen'...
→ ✓ Found: VWAGY — Volkswagen AG (OTC)
→ 📊 Running full analysis...
```

No hardcoded company list. No mapping files. Just ask naturally.

---

## 🚀 Quick Start

### 1. Install

```bash
pip install agent-framework requests python-dotenv fastmcp pydantic
pip install ddgs feedparser aiohttp botbuilder-core
```

### 2. Configure `.env`

```env
# Azure OpenAI (required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_FAST_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_REASONING_DEPLOYMENT=gpt-4o

# Financial Modeling Prep (required) — financialmodelingprep.com
FMP_API_KEY=your-fmp-key

# NewsAPI (recommended, free) — newsapi.org
NEWSAPI_KEY=your-newsapi-key

# Alpha Vantage (optional fallback) — alphavantage.co
ALPHA_VANTAGE_API_KEY=your-av-key

# Microsoft Teams (only for Teams deployment)
MICROSOFT_APP_ID=your-app-id
MICROSOFT_APP_PASSWORD=your-client-secret
```

### 3. Run

```bash
python magentic_agent_enhanced.py
```

```
💬 You: hello
🤖 👋 Hello! I'm your AI Financial Advisor. Just ask naturally!

💬 You: tell me about Palantir
→ 🔍 Searching for 'palantir'...
→ ✓ Found: PLTR — Palantir Technologies (NASDAQ)
→ 📊 Analyzing PLTR...

💬 You: should I buy it?
🤖 Based on my analysis of PLTR... ✅ Recommendation: Buy
```

---

## 💬 Conversational Interface

No commands. No menus. Just natural language.

| What you say | What happens |
|---|---|
| `"hello"` / `"hi"` / `"helo"` | Friendly greeting, no accidental analysis |
| `"Analyze Volkswagen"` | Finds VWAGY, runs full analysis |
| `"Tell me about Palantir"` | Finds PLTR, gives research overview |
| `"Latest news about BMW"` | Searches and displays recent news |
| `"Should I buy Tesla?"` | Full analysis + investment recommendation |
| `"What is the ticker of Porsche?"` | Looks up ticker live via FMP |
| `"Why?"` / `"Tell me more"` | Context-aware follow-up using previous analysis |
| `"Analyze S&P 500"` | ETF/index analysis (SPY) |
| `"Compare Apple vs Microsoft"` | Side-by-side comparison |

---

## 🔍 Smart Ticker Resolution

The agent **never uses a hardcoded company map**. It resolves any company dynamically:

```
Step 1 → Explicit patterns   $AAPL · (TSLA) · bare CAPS like "VW"
Step 2 → Index shorthands    S&P 500 → SPY · Nasdaq → QQQ · Dow → DIA
Step 3 → FMP live search     50,000+ symbols worldwide
Step 4 → Web fallback        DuckDuckGo + Google News RSS
```

This means it works for **any company in any country**, including new listings.

---

## 📊 ETF & Index Support

Ask about any major index or ETF by name:

| Indices | Sector ETFs | Commodity | Popular |
|---|---|---|---|
| S&P 500 → SPY | Technology → XLK | Gold → GLD | ARK Innovation → ARKK |
| Nasdaq → QQQ | Healthcare → XLV | Oil → USO | Vanguard Total → VTI |
| Dow Jones → DIA | Financials → XLF | Treasury → TLT | Emerging Markets → EEM |
| Russell 2000 → IWM | Energy → XLE | Bonds → AGG | Real Estate → VNQ |

---

## 📰 News & Sentiment

Every analysis automatically aggregates news from multiple sources:

```
FMP stock news          → 12–20 articles
+ NewsAPI               → Bloomberg, Reuters, CNBC, WSJ (free key required)
+ Google News RSS       → always available, no key needed
─────────────────────────────────────────────────
Total                   → 20–30 deduplicated articles per analysis
```

### Sentiment Analysis

The agent analyzes article **content** (not just titles) using explicit rules:

- **Positive** → earnings beat, revenue growth, analyst upgrades, keywords: *surge, rally, beat, outperform*
- **Negative** → earnings miss, layoffs, downgrades, keywords: *plunge, tumble, miss, decline, weak*
- **Threshold** → 60%+ positive = Positive · 60%+ negative = Negative · mixed = Neutral

---

## 🏗️ Architecture

```
User input (natural language)
        │
        ▼
[Intent Detection]
   greeting / news / analyze / research / recommendation / ticker_lookup
        │
        ▼
[Ticker Resolution]
   Explicit → FMP live search → Web fallback
        │
        ▼
[Financial Pipeline]
   InitAgent → EntityAgent → NewsAgent → SentimentAgent
        → FinancialDataAgent → FinancialAnalysisAgent
        │
        ▼
[Conversational Response]  →  Terminal / Microsoft Teams
```

### Core Files

| File | Purpose |
|---|---|
| `magentic_agent_enhanced.py` | **Run this.** Conversational loop, intent detection, ticker resolution |
| `tools_enhanced.py` | 24 financial tools (FMP + Alpha Vantage + web search) |
| `financial_agents.py` | FinancialDataAgent + FinancialAnalysisAgent (strict JSON output) |
| `sentiment_agent_enhanced.py` | Enhanced sentiment with positive/negative rules |
| `chat_client_factory.py` | Azure OpenAI client factory |
| `agent_dependencies.py` | Configuration and dependency injection |
| `teams_bot.py` | Microsoft Teams bot wrapper |
| `app_teams.py` | Teams bot server (aiohttp, port 3978) |

### Agent Files

| File | Role |
|---|---|
| `init_agent.py` | Create unique session GUID |
| `entity_agent.py` | Enrich company data (ticker, ISIN, description) |
| `fetch_news.py` | Fetch FMP stock news |
| `inspector_agent.py` | Data quality validation |
| `orchestrator_decision_agent.py` | Workflow decisions |

---

## 🛠️ Tools (24 Total)

### FMP API (13 tools)
`fmp_get_profile` · `fmp_quote` · `fmp_search_symbol` · `fmp_get_financials` · `fmp_get_key_metrics` · `fmp_get_ratios` · `fmp_get_historical_prices` · `fmp_stock_news` · `fmp_get_analyst_estimates` · `fmp_get_insider_trading` · `fmp_get_institutional_holders` · `fmp_get_sec_filings` · `fmp_get_earnings_calendar`

### Alpha Vantage Fallback (8 tools)
`av_get_quote` · `av_get_company_overview` · `av_get_income_statement` · `av_get_balance_sheet` · `av_get_cash_flow` · `av_get_time_series_daily` · `av_search_symbol` · `av_get_earnings`

### Web Search (3 tools)
`web_search_news` · `web_search_general` · `web_fetch_url`

---

## 🚀 Microsoft Teams Deployment

```
Teams User → Teams App
                │
          app_teams.py    (Azure App Service, port 3978)
                │
          teams_bot.py    (per-user conversation threading)
                │
    magentic_agent_enhanced.py
```

**Deploy in 5 steps:**

```bash
# 1. Register bot in Azure Portal → get App ID + Secret
# 2. Add to .env
MICROSOFT_APP_ID=your-app-id
MICROSOFT_APP_PASSWORD=your-client-secret

# 3. Deploy to Azure App Service
az webapp up --name your-bot --runtime PYTHON:3.11

# 4. Set endpoint in Azure Portal
#    https://your-app.azurewebsites.net/api/messages

# 5. Enable Teams channel → publish
```

---

## ⚙️ Configuration

### Azure OpenAI Models

| Setup | Chat | Fast | Reasoning |
|---|---|---|---|
| **Recommended** | gpt-4o | gpt-4o-mini | gpt-4o |
| Budget | gpt-4o-mini | gpt-4o-mini | gpt-4o-mini |
| Premium | gpt-4o | gpt-4o-mini | o1-preview |

### Storage (auto-created on first run)

```env
FINANCE_STATE_DIR=agent_state        # Session objects
FINANCE_ARTICLES_DIR=agent_articles  # News cache
FINANCIAL_DATA_DIR=financial_data    # Financial data cache
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `401 Authentication Error` | Check `AZURE_OPENAI_ENDPOINT` ends with `/`. Verify key and deployment names. |
| Agent returns markdown instead of JSON | Use the updated `financial_agents.py` (strict JSON output version). |
| `RuntimeWarning: duckduckgo_search renamed` | `pip uninstall duckduckgo-search && pip install ddgs` |
| Ticker not found | Try full company name, add country hint e.g. `"Volkswagen Germany"`, or use ticker directly. |
| FMP 404 for ETF news | Normal — system automatically uses web news (NewsAPI / Google News). |
| Sentiment loops 5–10x for ETFs | Normal for ETFs with sparse news. Pipeline still completes. |
| `Rate limit exceeded` | FMP free: 300 calls/day. Alpha Vantage free: 25 calls/day. |

---

## ✅ Production Checklist

- [ ] All API keys set in `.env`
- [ ] Azure OpenAI models deployed
- [ ] `pip install ddgs` (not `duckduckgo-search`)
- [ ] `NEWSAPI_KEY` set for best news quality
- [ ] `sentiment_agent.py` replaced with `sentiment_agent_enhanced.py`
- [ ] `financial_agents.py` is the strict-JSON version
- [ ] `python setup_verification.py` passes
- [ ] `python test_azure_connection.py` passes

---

## 📦 Requirements

```txt
# Core
agent-framework
requests
python-dotenv
fastmcp
pydantic

# Web search — use NEW package name
ddgs              # NOT duckduckgo-search
feedparser

# Teams deployment
botbuilder-core
botbuilder-schema
aiohttp

# Optional UI
gradio
streamlit
```

**Python 3.10+ required** (3.11+ recommended)

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
  <strong>Version 3.0 · February 2026 · Python 3.10+ · Production Ready ✅</strong>
</div>
