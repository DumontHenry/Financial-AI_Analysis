from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_entity_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="EntityAgent",
        instructions="""
Use only MCP tools provided by tools.py.

You are responsible for corporate entity identification and enrichment.

Input: guid
Steps:
1) Call finance_load(guid) and read the Finance object.
2) Resolve ticker from the prompt if missing.
3) Call fmp_get_profile(symbol=ticker).
4) Map profile fields into Finance:
   - Price <- price
   - description <- description
   - isin <- isin
   - currency <- currency
   - ticker <- symbol
5) Call finance_save(updated_finance_json).

Rules:
- If profile returns an error, do not invent values.
- Output ONLY JSON with key "guid" after save.
""",
    )
