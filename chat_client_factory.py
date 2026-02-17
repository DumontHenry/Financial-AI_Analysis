import os
from dotenv import load_dotenv

from agent_framework.azure import AzureOpenAIChatClient

# CRITICAL: Load environment variables BEFORE anything else
load_dotenv(override=True)


def build_chat_client(model_type: str = "standard") -> AzureOpenAIChatClient:
    # Explicitly load credentials from environment
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    
    # Determine which deployment to use
    if model_type == "fast":
        deployment = os.getenv(
            "AZURE_OPENAI_FAST_DEPLOYMENT",
            os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        )
    elif model_type == "reasoning":
        deployment = os.getenv(
            "AZURE_OPENAI_REASONING_DEPLOYMENT",
            os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        )
    else:
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    
    # Validate required variables
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT not set in environment")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY not set in environment")
    if not deployment:
        raise ValueError(f"Deployment name not set for model_type={model_type}")
    
    # Set environment variables that agent_framework expects
    os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    os.environ["AZURE_OPENAI_API_VERSION"] = api_version
    
    # Create client with explicit deployment name
    return AzureOpenAIChatClient(deployment_name=deployment)
