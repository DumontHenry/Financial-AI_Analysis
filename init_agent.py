from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient


def build_init_agent(chat_client: AzureOpenAIChatClient) -> ChatAgent:
    return ChatAgent(
        chat_client=chat_client,
        name="InitAgent",
        instructions="""
Use only MCP tools provided by tools.py.

Task:
- Call finance_init(prompt) to create shared Finance state.
- Output ONLY JSON: {"guid":"..."}.
- No markdown and no extra text.
""",
    )
