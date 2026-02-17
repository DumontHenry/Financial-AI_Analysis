from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_news_fetch_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="NewsFetchAgent",
        instructions="""
Use only MCP tools provided by tools.py.

Input: guid

Steps:
1) Call finance_load(guid).
2) If Finance.ticker is missing, output {"guid":"...", "stored": false, "error":"No ticker defined"}.
3) Call fmp_stock_news(Finance.ticker, limit=20).
4) If API response has "error", return it in output.
5) Otherwise call articles_save(guid, <news_json>).

Output ONLY JSON:
{"guid":"...", "stored": true|false, "article_count": <count>, "error": <error_msg_or_null>}
""",
    )

