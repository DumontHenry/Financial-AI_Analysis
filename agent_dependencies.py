"""
Agent dependencies and configuration for the financial agent system.
"""
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator agent system."""
    
    # Maximum orchestration loop iterations
    max_loops: int = 10
    
    # Required fields that must be populated
    required_fields: List[str] = field(default_factory=lambda: [
        "guid",
        "ticker",
        "description",
        "currency",
        "isin",
        "News_Sentiment"
    ])
    
    # MCP tools file location
    tools_file: str = "tools.py"
    
    # Storage directories
    articles_dir: Optional[Path] = field(default_factory=lambda: Path("agent_articles"))
    state_dir: Optional[Path] = field(default_factory=lambda: Path("agent_state"))
    financial_data_dir: Optional[Path] = field(default_factory=lambda: Path("financial_data"))
    
    # Agent timeout settings (seconds)
    agent_timeout: int = 120
    
    # Retry settings
    max_retries: int = 3
    retry_delay: int = 2
    
    def __post_init__(self):
        """Ensure directories exist."""
        if self.articles_dir:
            self.articles_dir.mkdir(parents=True, exist_ok=True)
        if self.state_dir:
            self.state_dir.mkdir(parents=True, exist_ok=True)
        if self.financial_data_dir:
            self.financial_data_dir.mkdir(parents=True, exist_ok=True)


# Default configuration instance
DEFAULT_CONFIG = OrchestratorConfig()
