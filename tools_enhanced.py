from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables immediately to ensure subprocess sees them
load_dotenv()

mcp = FastMCP("finance_tools")
FMP_BASE_URL = "https://financialmodelingprep.com"

# ----------------------------
# Models + local state store
# ----------------------------

class Finance(BaseModel):
    prompt: Optional[str] = Field(default=None)
    guid: Optional[str] = Field(default=None)
    ticker: Optional[str] = Field(default=None)
    value: Optional[float] = Field(default=None)
    date: Optional[str] = Field(default=None)
    currency: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    isin: Optional[str] = Field(default=None)
    Position: Optional[str] = Field(default=None)
    Quantity: Optional[int] = Field(default=None)
    Price: Optional[float] = Field(default=None)
    News_Sentiment: Optional[str] = Field(default=None)
    Urls: Optional[List[str]] = Field(default=None)
    # Extended fields for comprehensive analysis
    marketCap: Optional[float] = Field(default=None)
    beta: Optional[float] = Field(default=None)
    peRatio: Optional[float] = Field(default=None)
    eps: Optional[float] = Field(default=None)
    dividendYield: Optional[float] = Field(default=None)
    sector: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    exchange: Optional[str] = Field(default=None)

STATE_DIR = Path(os.getenv("FINANCE_STATE_DIR", "agent_state"))
STATE_DIR.mkdir(parents=True, exist_ok=True)

ARTICLES_DIR = Path(os.getenv("FINANCE_ARTICLES_DIR", "agent_articles"))
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

FINANCIAL_DATA_DIR = Path(os.getenv("FINANCIAL_DATA_DIR", "financial_data"))
FINANCIAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Helpers
# ----------------------------
def _extract_json_obj(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found.")
    return json.loads(m.group(0))

def _extract_json_any(text: str) -> Any:
    text = (text or "").strip()
    if (text.startswith("{") and text.endswith("}")) or (text.startswith("[") and text.endswith("]")):
        return json.loads(text)
    m = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object/array found.")
    return json.loads(m.group(0))

def _normalize_symbols(symbols: str) -> List[str]:
    if not symbols:
        return []
    parts = re.split(r"[,\s]+", symbols.strip())
    out: List[str] = []
    seen = set()
    for p in parts:
        s = p.strip().upper()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out

def _group_articles_by_symbol(articles: List[Dict[str, Any]], requested: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {s: [] for s in requested}
    for item in articles:
        item_symbols = item.get("symbols") or item.get("symbol")
        if isinstance(item_symbols, list):
            for sym in item_symbols:
                su = str(sym).upper()
                if su in grouped:
                    grouped[su].append(item)
        elif isinstance(item_symbols, str):
            su = item_symbols.upper()
            if su in grouped:
                grouped[su].append(item)
    return grouped

def _articles_path(guid: str) -> Path:
    return ARTICLES_DIR / f"{guid}_articles.json"

def _financial_data_path(guid: str, data_type: str) -> Path:
    return FINANCIAL_DATA_DIR / f"{guid}_{data_type}.json"

# ----------------------------
# MCP tools: Finance state
# ----------------------------

@mcp.tool()
def finance_init(prompt: str) -> str:
    """Initialize a new Finance state object with a unique GUID."""
    fin = Finance(
        prompt=prompt,
        guid=str(uuid.uuid4()),
        date=datetime.utcnow().date().isoformat(),
    )
    path = STATE_DIR / f"{fin.guid}.json"
    path.write_text(fin.model_dump_json(indent=2), encoding="utf-8")
    return json.dumps({"guid": fin.guid}, ensure_ascii=False)

@mcp.tool()
def finance_load(guid: str) -> str:
    """Load a Finance state object by GUID."""
    path = STATE_DIR / f"{guid}.json"
    if not path.exists():
        return json.dumps({"error": f"No Finance state found for guid={guid}"}, ensure_ascii=False)
    return path.read_text(encoding="utf-8")

@mcp.tool()
def finance_save(finance_json: str) -> str:
    """Save or update a Finance state object."""
    try:
        data = _extract_json_obj(finance_json)
        fin = Finance.model_validate(data)

        if not fin.guid:
            fin.guid = str(uuid.uuid4())
        if not fin.date:
            fin.date = datetime.utcnow().date().isoformat()

        path = STATE_DIR / f"{fin.guid}.json"
        path.write_text(fin.model_dump_json(indent=2), encoding="utf-8")
        return json.dumps({"guid": fin.guid}, ensure_ascii=False)
    except Exception as e:
         return json.dumps({"error": str(e)}, ensure_ascii=False)

# ----------------------------
# MCP tools: FinancialModelingPrep (FMP) API
# ----------------------------

def _fmp_key() -> Optional[str]:
    """Retrieve FMP API key from environment."""
    return os.getenv("FMP_API_KEY")

def _alpha_vantage_key() -> Optional[str]:
    """Retrieve Alpha Vantage API key from environment."""
    return os.getenv("ALPHA_VANTAGE_API_KEY")

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

@mcp.tool()
def fmp_healthcheck(symbol: str = "AAPL") -> str:
    """Check if FMP API is accessible and responding."""
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"ok": False, "error": "FMP_API_KEY not set in environment"}, ensure_ascii=False)

    url = f"{FMP_BASE_URL}/stable/quote"
    params = {"symbol": symbol.upper().strip(), "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=20)
        return json.dumps(
            {"ok": r.status_code == 200, "status_code": r.status_code},
            ensure_ascii=False
        )
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def fmp_get_profile(symbol: str) -> str:
    """
    Get complete company profile from FMP API.
    Returns: price, marketCap, description, isin, industry, sector, etc.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/profile"
    params = {
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            return json.dumps(data[0], ensure_ascii=False)
        return json.dumps({"error": f"No profile found for {symbol}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_search_symbol(query: str, limit: int = 5) -> str:
    """Search for stock symbols by company name or ticker."""
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"query": query, "results": [], "error": "FMP_API_KEY not set"}, ensure_ascii=False)

    url = f"{FMP_BASE_URL}/stable/search-symbol"
    params = {"query": query, "limit": int(limit), "apikey": api_key}

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()

        data = r.json()
        items = data if isinstance(data, list) else []

        out = []
        for it in items:
            out.append({
                "symbol": it.get("symbol"),
                "name": it.get("name"),
                "exchange": it.get("exchange"),
                "currency": it.get("currency"),
                "type": it.get("type"),
            })

        return json.dumps({"query": query, "results": out}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"query": query, "results": [], "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def fmp_quote(symbol: str) -> str:
    """Get real-time quote for a stock symbol."""
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"symbol": symbol, "error": "FMP_API_KEY not set"}, ensure_ascii=False)

    url = f"{FMP_BASE_URL}/stable/quote"
    params = {"symbol": symbol.upper().strip(), "apikey": api_key}

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()

        data = r.json()
        q = (data[0] if isinstance(data, list) and data else {}) or {}

        if not q:
             return json.dumps({"symbol": symbol, "error": "Symbol not found or API error"}, ensure_ascii=False)

        out = {
            "symbol": q.get("symbol"),
            "name": q.get("name"),
            "price": q.get("price"),
            "currency": q.get("currency"),
            "marketCap": q.get("marketCap"),
            "changePercentage": q.get("changePercentage"),
            "change": q.get("change"),
            "dayLow": q.get("dayLow"),
            "dayHigh": q.get("dayHigh"),
            "yearLow": q.get("yearLow"),
            "yearHigh": q.get("yearHigh"),
            "volume": q.get("volume"),
            "avgVolume": q.get("avgVolume"),
            "open": q.get("open"),
            "previousClose": q.get("previousClose"),
            "eps": q.get("eps"),
            "pe": q.get("pe"),
        }
        return json.dumps(out, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def fmp_stock_news(symbols: str, limit: int = 20, page: int = 0) -> str:
    """Fetch stock news for given symbols from FMP API."""
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"symbols": [], "articles_by_symbol": {}, "error": "FMP_API_KEY not set"}, ensure_ascii=False)

    sym_list = _normalize_symbols(symbols)
    if not sym_list:
        return json.dumps({"error": "No symbols provided"}, ensure_ascii=False)

    url = f"{FMP_BASE_URL}/stable/stock_news"
    params = {"symbols": ",".join(sym_list), "limit": int(limit), "page": int(page), "apikey": api_key}

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()

        data = r.json()
        articles = data if isinstance(data, list) else []
        grouped = _group_articles_by_symbol(articles, sym_list)

        return json.dumps(
            {"symbols": sym_list, "article_count": len(articles),
             "articles_by_symbol": grouped, "raw": articles},
            ensure_ascii=False
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# ----------------------------
# NEW: Enhanced Financial Data Tools
# ----------------------------

@mcp.tool()
def fmp_get_financials(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Get financial statements (income statement, balance sheet, cash flow).
    
    Args:
        symbol: Stock ticker symbol
        period: 'annual' or 'quarter'
        limit: Number of periods to retrieve
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    symbol_clean = symbol.upper().strip()
    
    # Get all three financial statements
    statements: Dict[str, Any] = {}
    endpoints = {
        "income_statement": f"{FMP_BASE_URL}/stable/income-statement",
        "balance_sheet": f"{FMP_BASE_URL}/stable/balance-sheet-statement",
        "cash_flow": f"{FMP_BASE_URL}/stable/cash-flow-statement"
    }
    
    try:
        for stmt_name, url in endpoints.items():
            params = {"symbol": symbol_clean, "period": period, "limit": limit, "apikey": api_key}
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            statements[stmt_name] = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol_clean,
            "period": period,
            "statements": statements
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_key_metrics(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Get key financial metrics and ratios.
    
    Includes: P/E, ROE, ROA, profit margins, debt ratios, etc.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/key-metrics"
    params = {
        "symbol": symbol.upper().strip(),
        "period": period,
        "limit": limit,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        metrics = data if isinstance(data, list) else []
        return json.dumps({
            "symbol": symbol,
            "period": period,
            "metrics": metrics
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_ratios(symbol: str, period: str = "annual", limit: int = 5) -> str:
    """
    Get financial ratios including liquidity, profitability, and efficiency ratios.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/ratios"
    params = {
        "symbol": symbol.upper().strip(),
        "period": period,
        "limit": limit,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        return json.dumps({
            "symbol": symbol,
            "period": period,
            "ratios": data if isinstance(data, list) else []
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_historical_prices(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> str:
    """
    Get historical stock prices.
    
    Args:
        symbol: Stock ticker
        from_date: Start date (YYYY-MM-DD), defaults to 1 year ago
        to_date: End date (YYYY-MM-DD), defaults to today
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    if not from_date:
        from_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")

    url = f"{FMP_BASE_URL}/stable/historical-price-full/{symbol.upper().strip()}"
    params = {
        "from": from_date,
        "to": to_date,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        historical = data.get("historical", []) if isinstance(data, dict) else []
        
        return json.dumps({
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "data_points": len(historical),
            "historical": historical
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_analyst_estimates(symbol: str, period: str = "annual", limit: int = 4) -> str:
    """
    Get analyst estimates for revenue and earnings.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/analyst-estimates"
    params = {
        "symbol": symbol.upper().strip(),
        "period": period,
        "limit": limit,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        return json.dumps({
            "symbol": symbol,
            "period": period,
            "estimates": data if isinstance(data, list) else []
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_insider_trading(symbol: str, limit: int = 50) -> str:
    """
    Get insider trading activity for a stock.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/insider-trading"
    params = {
        "symbol": symbol.upper().strip(),
        "limit": limit,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        trades = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol,
            "trade_count": len(trades),
            "trades": trades
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_institutional_holders(symbol: str) -> str:
    """
    Get institutional holders and their positions.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/institutional-holder"
    params = {
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        holders = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol,
            "holder_count": len(holders),
            "holders": holders
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_sec_filings(symbol: str, filing_type: Optional[str] = None, limit: int = 20) -> str:
    """
    Get SEC filings (10-K, 10-Q, 8-K, etc.) for a company.
    
    Args:
        symbol: Stock ticker
        filing_type: Filter by type (10-K, 10-Q, 8-K, etc.), None for all
        limit: Number of filings to retrieve
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/sec_filings"
    params: Dict[str, Any] = {
        "symbol": symbol.upper().strip(),
        "limit": limit,
        "apikey": api_key
    }
    
    if filing_type:
        params["type"] = filing_type.upper()

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        filings = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol,
            "filing_type": filing_type,
            "filing_count": len(filings),
            "filings": filings
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_earnings_calendar(symbol: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None) -> str:
    """
    Get earnings calendar. Can filter by symbol or date range.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/earning_calendar"
    params: Dict[str, Any] = {"apikey": api_key}
    
    if symbol:
        params["symbol"] = symbol.upper().strip()
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        calendar = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "event_count": len(calendar),
            "events": calendar
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fmp_get_market_cap_history(symbol: str, limit: int = 100) -> str:
    """
    Get historical market capitalization data.
    """
    api_key = _fmp_key()
    if not api_key:
        return json.dumps({"error": "FMP_API_KEY not set"})

    url = f"{FMP_BASE_URL}/stable/historical-market-capitalization"
    params = {
        "symbol": symbol.upper().strip(),
        "limit": limit,
        "apikey": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        history = data if isinstance(data, list) else []
        
        return json.dumps({
            "symbol": symbol,
            "data_points": len(history),
            "history": history
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})

# ----------------------------
# Generic Web Scraping Tools
# ----------------------------

@mcp.tool()
def web_fetch_json(url: str, headers: Optional[str] = None, params: Optional[str] = None) -> str:
    """
    Generic JSON API fetcher for financial websites.
    
    Args:
        url: API endpoint URL
        headers: JSON string of headers (optional)
        params: JSON string of query parameters (optional)
    """
    try:
        req_headers: Dict[str, Any] = json.loads(headers) if headers else {}
        req_params: Dict[str, Any] = json.loads(params) if params else {}
        
        r = requests.get(url, headers=req_headers, params=req_params, timeout=30)
        r.raise_for_status()
        
        data = r.json()
        
        return json.dumps({
            "url": url,
            "status_code": r.status_code,
            "data": data
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"url": url, "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def web_fetch_html(url: str) -> str:
    """
    Fetch HTML content from a webpage for scraping.
    Returns the raw HTML text.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        
        return json.dumps({
            "url": url,
            "status_code": r.status_code,
            "content_length": len(r.text),
            "html": r.text[:10000]  # First 10k chars to avoid huge payloads
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"url": url, "error": str(e)}, ensure_ascii=False)

# ----------------------------
# Data Storage Tools
# ----------------------------

@mcp.tool()
def articles_save(guid: str, articles_json: str) -> str:
    """Save articles data for a given GUID."""
    p = _articles_path(guid)
    try:
        data = _extract_json_any(articles_json)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return json.dumps({"path": str(p)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def articles_load(guid: str) -> str:
    """Load stored articles for a given GUID."""
    p = _articles_path(guid)
    if not p.exists():
        return json.dumps({"articles": [], "error": "No stored articles"}, ensure_ascii=False)
    return p.read_text(encoding="utf-8")

@mcp.tool()
def financial_data_save(guid: str, data_type: str, data_json: str) -> str:
    """
    Save financial data of a specific type for a GUID.
    
    Args:
        guid: Unique identifier
        data_type: Type of data (financials, ratios, prices, etc.)
        data_json: JSON data to save
    """
    p = _financial_data_path(guid, data_type)
    try:
        data = _extract_json_any(data_json)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return json.dumps({"path": str(p), "data_type": data_type}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

@mcp.tool()
def financial_data_load(guid: str, data_type: str) -> str:
    """
    Load financial data of a specific type for a GUID.
    """
    p = _financial_data_path(guid, data_type)
    if not p.exists():
        return json.dumps({"error": f"No {data_type} data found for guid={guid}"}, ensure_ascii=False)
    return p.read_text(encoding="utf-8")

@mcp.tool()
def list_saved_data(guid: str) -> str:
    """
    List all saved data files for a given GUID.
    """
    try:
        files = []
        
        # Check finance state
        state_file = STATE_DIR / f"{guid}.json"
        if state_file.exists():
            files.append({"type": "finance_state", "path": str(state_file)})
        
        # Check articles
        articles_file = _articles_path(guid)
        if articles_file.exists():
            files.append({"type": "articles", "path": str(articles_file)})
        
        # Check financial data
        for file in FINANCIAL_DATA_DIR.glob(f"{guid}_*.json"):
            data_type = file.stem.replace(f"{guid}_", "")
            files.append({"type": data_type, "path": str(file)})
        
        return json.dumps({
            "guid": guid,
            "file_count": len(files),
            "files": files
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

# ----------------------------
# Alpha Vantage MCP Tools (Fallback/Supplementary Data Source)
# ----------------------------

@mcp.tool()
def av_healthcheck() -> str:
    """Check if Alpha Vantage API is accessible."""
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"ok": False, "error": "ALPHA_VANTAGE_API_KEY not set in environment"}, ensure_ascii=False)

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "IBM",
        "apikey": api_key
    }
    
    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        return json.dumps(
            {"ok": r.status_code == 200, "status_code": r.status_code},
            ensure_ascii=False
        )
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)

@mcp.tool()
def av_get_quote(symbol: str) -> str:
    """
    Get real-time quote from Alpha Vantage.
    Alternative/fallback to FMP quote data.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        quote = data.get("Global Quote", {})
        
        if not quote:
            return json.dumps({"symbol": symbol, "error": "No data returned from Alpha Vantage"})
        
        return json.dumps({
            "symbol": quote.get("01. symbol"),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "changePercent": quote.get("10. change percent", "0%").replace("%", ""),
            "volume": int(quote.get("06. volume", 0)),
            "latestTradingDay": quote.get("07. latest trading day"),
            "previousClose": float(quote.get("08. previous close", 0)),
            "open": float(quote.get("02. open", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_get_company_overview(symbol: str) -> str:
    """
    Get company overview and fundamental data from Alpha Vantage.
    Alternative/fallback to FMP profile data.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "OVERVIEW",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        if not data or "Symbol" not in data:
            return json.dumps({"symbol": symbol, "error": "No overview data available"})
        
        return json.dumps({
            "symbol": data.get("Symbol"),
            "name": data.get("Name"),
            "description": data.get("Description"),
            "sector": data.get("Sector"),
            "industry": data.get("Industry"),
            "exchange": data.get("Exchange"),
            "currency": data.get("Currency"),
            "country": data.get("Country"),
            "marketCap": float(data.get("MarketCapitalization", 0)) if data.get("MarketCapitalization") else None,
            "peRatio": float(data.get("PERatio", 0)) if data.get("PERatio") else None,
            "eps": float(data.get("EPS", 0)) if data.get("EPS") else None,
            "dividendYield": float(data.get("DividendYield", 0)) if data.get("DividendYield") else None,
            "beta": float(data.get("Beta", 0)) if data.get("Beta") else None,
            "week52High": float(data.get("52WeekHigh", 0)) if data.get("52WeekHigh") else None,
            "week52Low": float(data.get("52WeekLow", 0)) if data.get("52WeekLow") else None,
            "day50MovingAverage": float(data.get("50DayMovingAverage", 0)) if data.get("50DayMovingAverage") else None,
            "day200MovingAverage": float(data.get("200DayMovingAverage", 0)) if data.get("200DayMovingAverage") else None,
            "analystTargetPrice": float(data.get("AnalystTargetPrice", 0)) if data.get("AnalystTargetPrice") else None,
            "profitMargin": float(data.get("ProfitMargin", 0)) if data.get("ProfitMargin") else None,
            "operatingMargin": float(data.get("OperatingMarginTTM", 0)) if data.get("OperatingMarginTTM") else None,
            "returnOnAssets": float(data.get("ReturnOnAssetsTTM", 0)) if data.get("ReturnOnAssetsTTM") else None,
            "returnOnEquity": float(data.get("ReturnOnEquityTTM", 0)) if data.get("ReturnOnEquityTTM") else None,
            "revenuePerShare": float(data.get("RevenuePerShareTTM", 0)) if data.get("RevenuePerShareTTM") else None,
            "quarterlyEarningsGrowth": float(data.get("QuarterlyEarningsGrowthYOY", 0)) if data.get("QuarterlyEarningsGrowthYOY") else None,
            "quarterlyRevenueGrowth": float(data.get("QuarterlyRevenueGrowthYOY", 0)) if data.get("QuarterlyRevenueGrowthYOY") else None,
            "bookValue": float(data.get("BookValue", 0)) if data.get("BookValue") else None,
            "priceToBook": float(data.get("PriceToBookRatio", 0)) if data.get("PriceToBookRatio") else None,
            "evToRevenue": float(data.get("EVToRevenue", 0)) if data.get("EVToRevenue") else None,
            "evToEbitda": float(data.get("EVToEBITDA", 0)) if data.get("EVToEBITDA") else None,
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_get_income_statement(symbol: str) -> str:
    """
    Get annual income statements from Alpha Vantage.
    Alternative/fallback to FMP financial statements.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        annual_reports = data.get("annualReports", [])
        quarterly_reports = data.get("quarterlyReports", [])
        
        return json.dumps({
            "symbol": data.get("symbol", symbol),
            "annual_reports": annual_reports[:5],  # Last 5 years
            "quarterly_reports": quarterly_reports[:4],  # Last 4 quarters
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_get_balance_sheet(symbol: str) -> str:
    """
    Get annual balance sheets from Alpha Vantage.
    Alternative/fallback to FMP financial statements.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "BALANCE_SHEET",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        annual_reports = data.get("annualReports", [])
        quarterly_reports = data.get("quarterlyReports", [])
        
        return json.dumps({
            "symbol": data.get("symbol", symbol),
            "annual_reports": annual_reports[:5],
            "quarterly_reports": quarterly_reports[:4],
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_get_cash_flow(symbol: str) -> str:
    """
    Get annual cash flow statements from Alpha Vantage.
    Alternative/fallback to FMP financial statements.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "CASH_FLOW",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        annual_reports = data.get("annualReports", [])
        quarterly_reports = data.get("quarterlyReports", [])
        
        return json.dumps({
            "symbol": data.get("symbol", symbol),
            "annual_reports": annual_reports[:5],
            "quarterly_reports": quarterly_reports[:4],
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_get_time_series_daily(symbol: str, outputsize: str = "compact") -> str:
    """
    Get daily historical stock prices from Alpha Vantage.
    
    Args:
        symbol: Stock ticker
        outputsize: 'compact' (100 days) or 'full' (20+ years)
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol.upper().strip(),
        "outputsize": outputsize,
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        time_series = data.get("Time Series (Daily)", {})
        
        if not time_series:
            return json.dumps({"symbol": symbol, "error": "No time series data available"})
        
        # Convert to list format for easier processing
        historical = []
        for date, values in sorted(time_series.items(), reverse=True):
            historical.append({
                "date": date,
                "open": float(values.get("1. open", 0)),
                "high": float(values.get("2. high", 0)),
                "low": float(values.get("3. low", 0)),
                "close": float(values.get("4. close", 0)),
                "adjusted_close": float(values.get("5. adjusted close", 0)),
                "volume": int(values.get("6. volume", 0)),
                "dividend_amount": float(values.get("7. dividend amount", 0)),
                "split_coefficient": float(values.get("8. split coefficient", 1.0))
            })
        
        return json.dumps({
            "symbol": symbol,
            "data_points": len(historical),
            "historical": historical,
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

@mcp.tool()
def av_search_symbol(keywords: str) -> str:
    """
    Search for stock symbols by company name using Alpha Vantage.
    Alternative/fallback to FMP symbol search.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keywords,
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        matches = data.get("bestMatches", [])
        
        results = []
        for match in matches[:10]:  # Top 10 results
            results.append({
                "symbol": match.get("1. symbol"),
                "name": match.get("2. name"),
                "type": match.get("3. type"),
                "region": match.get("4. region"),
                "currency": match.get("8. currency"),
                "matchScore": float(match.get("9. matchScore", 0))
            })
        
        return json.dumps({
            "keywords": keywords,
            "results": results,
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"keywords": keywords, "error": str(e)})

@mcp.tool()
def av_get_earnings(symbol: str) -> str:
    """
    Get quarterly and annual earnings data from Alpha Vantage.
    """
    api_key = _alpha_vantage_key()
    if not api_key:
        return json.dumps({"error": "ALPHA_VANTAGE_API_KEY not set"})

    params = {
        "function": "EARNINGS",
        "symbol": symbol.upper().strip(),
        "apikey": api_key
    }

    try:
        r = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        
        return json.dumps({
            "symbol": data.get("symbol", symbol),
            "annual_earnings": data.get("annualEarnings", []),
            "quarterly_earnings": data.get("quarterlyEarnings", [])[:8],  # Last 8 quarters
            "source": "Alpha Vantage"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"symbol": symbol, "error": str(e)})

# ----------------------------
# Hybrid Tools (Try FMP first, fallback to Alpha Vantage)
# ----------------------------

@mcp.tool()
def hybrid_get_quote(symbol: str) -> str:
    """
    Get stock quote with automatic fallback.
    Tries FMP first, falls back to Alpha Vantage if FMP fails.
    """
    # Try FMP first
    fmp_result = fmp_quote(symbol)
    fmp_data = json.loads(fmp_result)
    
    if "error" not in fmp_data and fmp_data.get("price"):
        fmp_data["source"] = "FMP (primary)"
        return json.dumps(fmp_data, ensure_ascii=False)
    
    # Fallback to Alpha Vantage
    av_result = av_get_quote(symbol)
    av_data = json.loads(av_result)
    
    if "error" not in av_data:
        av_data["source"] = "Alpha Vantage (fallback)"
        return json.dumps(av_data, ensure_ascii=False)
    
    # Both failed
    return json.dumps({
        "symbol": symbol,
        "error": "Failed to get quote from both FMP and Alpha Vantage",
        "fmp_error": fmp_data.get("error"),
        "av_error": av_data.get("error")
    })

@mcp.tool()
def hybrid_get_company_info(symbol: str) -> str:
    """
    Get company information with automatic fallback.
    Tries FMP first, falls back to Alpha Vantage if FMP fails.
    """
    # Try FMP first
    fmp_result = fmp_get_profile(symbol)
    fmp_data = json.loads(fmp_result)
    
    if "error" not in fmp_data and fmp_data.get("description"):
        fmp_data["source"] = "FMP (primary)"
        return json.dumps(fmp_data, ensure_ascii=False)
    
    # Fallback to Alpha Vantage
    av_result = av_get_company_overview(symbol)
    av_data = json.loads(av_result)
    
    if "error" not in av_data:
        av_data["source"] = "Alpha Vantage (fallback)"
        return json.dumps(av_data, ensure_ascii=False)
    
    # Both failed
    return json.dumps({
        "symbol": symbol,
        "error": "Failed to get company info from both FMP and Alpha Vantage",
        "fmp_error": fmp_data.get("error"),
        "av_error": av_data.get("error")
    })

if __name__ == "__main__":
    mcp.run()
