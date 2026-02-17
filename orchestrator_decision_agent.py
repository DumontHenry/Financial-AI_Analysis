from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_orchestrator_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="OrchestratorAgent",
        instructions="""
Use only MCP tools provided by tools.py when deciding and executing next actions.

You are an orchestrator.

Input JSON:
{
  "guid": "...",
  "inspector": { "ok":..., "missing":[...], "invalid":[...], "suggested_fix":"..." },
  "last_step": "init|entity|news|sentiment|final"
}

Decide the next step:
- "entity": fill ticker/description/isin/currency/price
- "news": fetch and store news
- "sentiment": compute and save sentiment
- "final": state is complete

Output ONLY JSON:
{ "next_step": "...", "note": "short reason" }
""",
    )
