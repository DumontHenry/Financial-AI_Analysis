# 🤖 Financial AI Agent System

> **Conversational AI financial advisor** — talk to it naturally, get institutional-grade analysis on any stock, ETF, or index worldwide.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-0078D4) ![FMP](https://img.shields.io/badge/Data-FMP%20%2B%20Web-green) ![Version](https://img.shields.io/badge/Version-3.0-orange)

---

## ✨ What Makes This Different

Unlike tools that require exact ticker symbols, this agent **finds any company dynamically**:

```
💬 You: Analyze Volkswagen
→ 🔍 Searching for 'volkswagen'...
→ ✓ Found: VWAGY — Volkswagen AG (OTC)
→ 📊 Running full analysis...

💬 You: Latest news about BMW
→ 🔍 Fetching news...
→ 📰 5 recent articles from Bloomberg, Reuters...

💬 You: Should I buy it?
→ ✅ Recommendation: Hold — here's why...
```

No hardcoded company list. No mapping files. Just ask naturally.

---

## 📁 Project Structure

```
FINANCIAL DATA /
│
├── agent_articles/          # News articles cache (auto-created)
├── agent_state/             # Session state files (auto-created)
├── financial_data/          # Financial data cache (auto-created)
│
├── .env                     # Your API keys (not committed)
├── agent_dependencies.py    # Configuration & dependency injection
├── chat_client_factory.py   # Azure OpenAI client factory
├── entity_agent.py          # Company data enrichment
├── fetch_news.py            # FMP + web news fetching
├── financial_agents.py      # FinancialDataAgent + FinancialAnalysisAgent
├── init_agent.py            # Session GUID creation
├── inspector_agent.py       # Data quality validation
├── magentic_agent_enhanced.py  ← RUN THIS
├── orchestrator_decision_agent.py  # Workflow decisions
├── README.md
├── requirements.txt
├── sentiment_agent_enhanced.py  # Enhanced sentiment analysis
├── setup_verification.py    # Full setup verification

└── tools_enhanced.py        # 24 financial data tools
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
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
```



### 3. Run

```bash
python magentic_agent_enhanced.py
```

---

## 💬 Conversational Interface

No commands. No menus. Just natural language.

| What you say | What happens |
|---|---|
| `"hello"` / `"hi"` / `"hey"` | Friendly greeting — no accidental analysis |
| `"Analyze Volkswagen"` | Finds VWAGY, runs full pipeline |
| `"Tell me about Palantir"` | Finds PLTR, gives research overview |
| `"Latest news about BMW"` | Fetches and displays recent articles |
| `"Should I buy Tesla?"` | Full analysis + investment recommendation |
| `"What is the ticker of Porsche?"` | Live lookup via FMP API |
| `"Why?"` / `"Tell me more"` | Context-aware follow-up |
| `"Analyze S&P 500"` | ETF/index analysis → SPY |
| `"Compare Apple vs Microsoft"` | Side-by-side comparison |

---

## 🔍 Smart Ticker Resolution

The agent **never uses a hardcoded company map**. Every name is resolved live:

```
Step 1 → Explicit patterns    $AAPL · (TSLA) · bare CAPS like "VW"
Step 2 → Index shorthands     S&P 500→SPY · Nasdaq→QQQ · Dow→DIA
Step 3 → FMP live search      50,000+ symbols worldwide
Step 4 → Web fallback         DuckDuckGo + Google News RSS
```

Works for **any company in any country**, including new listings and European/Asian stocks.

---

## 📊 ETF & Index Support

| Indices | Sector ETFs | Commodity | Popular |
|---|---|---|---|
| S&P 500 → SPY | Technology → XLK | Gold → GLD | ARK Innovation → ARKK |
| Nasdaq → QQQ | Healthcare → XLV | Oil → USO | Vanguard Total → VTI |
| Dow Jones → DIA | Financials → XLF | Treasury → TLT | Emerging Markets → EEM |
| Russell 2000 → IWM | Energy → XLE | Bonds → AGG | Real Estate → VNQ |

---

## 📰 News & Sentiment

Every analysis automatically aggregates from multiple sources:

```
FMP stock news        →  12–20 articles  (primary)
+ NewsAPI             →  Bloomberg, Reuters, CNBC, WSJ
+ Google News RSS     →  always available, no key needed
──────────────────────────────────────────────────────
Total                 →  20–30 deduplicated articles
```

**Sentiment rules** — analyzes article content, not just headlines:

- 🟢 **Positive** → earnings beat, growth, upgrades · keywords: *surge, rally, beat, outperform*
- 🔴 **Negative** → earnings miss, layoffs, downgrades · keywords: *plunge, miss, decline, weak*
- ⚪ **Neutral** → mixed or balanced signals
- **Threshold**: 60%+ in one direction → that sentiment wins

---

## 🏗️ How It Works

```
User input (natural language)
        │
        ▼
[Intent Detection]
  greeting · news · analyze · research · recommendation · ticker_lookup
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
[Conversational Response]
```

### Agent Roles

| Agent | File | Role |
|---|---|---|
| Init | `init_agent.py` | Create unique session GUID |
| Entity | `entity_agent.py` | Resolve ticker, ISIN, company description |
| News | `fetch_news.py` | Fetch FMP articles + web supplement |
| Sentiment | `sentiment_agent_enhanced.py` | Analyze news sentiment with explicit rules |
| Financial Data | `financial_agents.py` | Fetch profile, ratios, prices, statements |
| Financial Analysis | `financial_agents.py` | SWOT analysis + investment recommendation |
| Inspector | `inspector_agent.py` | Validate data quality |
| Orchestrator | `orchestrator_decision_agent.py` | Workflow decisions |

---

## 🛠️ Tools (24 Total)

### FMP API (13)
`fmp_get_profile` · `fmp_quote` · `fmp_search_symbol` · `fmp_get_financials` · `fmp_get_key_metrics` · `fmp_get_ratios` · `fmp_get_historical_prices` · `fmp_stock_news` · `fmp_get_analyst_estimates` · `fmp_get_insider_trading` · `fmp_get_institutional_holders` · `fmp_get_sec_filings` · `fmp_get_earnings_calendar`

### Alpha Vantage Fallback (8)
`av_get_quote` · `av_get_company_overview` · `av_get_income_statement` · `av_get_balance_sheet` · `av_get_cash_flow` · `av_get_time_series_daily` · `av_search_symbol` · `av_get_earnings`

### Web Search (3)
`web_search_news` · `web_search_general` · `web_fetch_url`

---

## ⚙️ Configuration

### Azure OpenAI Models

| Setup | Chat | Fast | Reasoning |
|---|---|---|---|
| **Recommended** | gpt-4o | gpt-4o-mini | gpt-4o |
| Budget | gpt-4o-mini | gpt-4o-mini | gpt-4o-mini |
| Premium | gpt-4o | gpt-4o-mini | o1-preview |

### Auto-created directories

```
agent_state/         # Finance session objects per GUID
agent_articles/      # News articles cache per GUID
financial_data/      # Financial data cache per GUID
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `401 Authentication Error` | Check `AZURE_OPENAI_ENDPOINT` ends with `/`. Verify key and deployment names. |
| Agent returns markdown not JSON | Use the updated `financial_agents.py` with strict JSON instructions. |
| `RuntimeWarning: duckduckgo_search renamed` | `pip uninstall duckduckgo-search && pip install ddgs` |
| Ticker not found | Try full company name or add country hint: `"Volkswagen Germany"` |
| FMP 404 for ETF news (SPY etc.) | Normal — falls back automatically to NewsAPI / Google News. |
| Sentiment loops 5–10x for ETFs | Normal for ETFs with sparse news. Pipeline still completes. |
| Rate limit exceeded | FMP free: 300 req/day · Alpha Vantage free: 25 req/day |

---

## ✅ Pre-flight Checklist


Before going to production:

- [ ] All API keys set in `.env`
- [ ] `pip install ddgs` (not `duckduckgo-search`)
- [ ] `NEWSAPI_KEY` configured for best news quality
- [ ] `sentiment_agent_enhanced.py` in use (not the original)
- [ ] `financial_agents.py` is the strict-JSON version
- [ ] All verification scripts pass

---

## 📦 Dependencies

```txt
# Core
agent-framework
requests
python-dotenv
fastmcp
pydantic

# Web search — NEW package name
ddgs              # replaces duckduckgo-search
feedparser

# Optional UI
gradio
streamlit
```

**Python 3.10+** required · 3.11+ recommended

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
  <strong>Version 3.0 · February 2026 · Python 3.10+ · Production Ready ✅</strong>
</div>
