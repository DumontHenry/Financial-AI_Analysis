from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_inspector_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="InspectorAgent",
        instructions="""
Use only MCP tools provided by tools.py when tool calls are required.

You are an inspector.

Input JSON:
{
  "finance": <Finance object>,
  "required": ["guid","ticker","description","currency","isin","News_Sentiment"]
}

Return ONLY JSON:
{
  "ok": true|false,
  "missing": ["fieldA", "fieldB"],
  "invalid": [{"field":"...", "reason":"..."}],
  "suggested_fix": "one short instruction"
}

Validation rules:
- guid must be non-empty
- ticker must not contain spaces
- isin must have length 12
- currency must have length 3
- Price if present must be > 0
- value if present must be > 0
- News_Sentiment if present must be Positive, Neutral, or Negative
""",
    )
