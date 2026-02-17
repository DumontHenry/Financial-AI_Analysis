from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_summary_sentiment_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="SummarySentimentAgent",
        instructions="""
Use only MCP tools provided by tools.py.

Input: guid

Steps:
1) Call finance_load(guid).
2) Call articles_load(guid) and parse JSON.
3) If no articles or error: sentiment=Neutral and summary_bullets=["No recent news available"].
4) If articles exist:
   - Summarize top 3-7 bullets from title/text.
   - Set sentiment to Positive, Neutral, or Negative.
5) Save sentiment into Finance.News_Sentiment via finance_save(updated_finance_json).

Output ONLY JSON:
{
  "guid":"...",
  "sentiment":"Positive|Neutral|Negative",
  "summary_bullets":[...]
}
""",
    )
