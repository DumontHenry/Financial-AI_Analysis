## Enhanced Magentic Agent with Financial Data Extraction
## Extends the original orchestration with comprehensive financial data tools

# CRITICAL: Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv(override=True)

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from agent_framework import MCPStdioTool

from agent_dependencies import OrchestratorConfig
from chat_client_factory import build_chat_client
from entity_agent import build_entity_agent
from fetch_news import build_news_fetch_agent
from init_agent import build_init_agent
from inspector_agent import build_inspector_agent
from orchestrator_decision_agent import build_orchestrator_agent
from sentiment_agent import build_summary_sentiment_agent
from financial_agents import (
    build_financial_data_agent,
    build_financial_analysis_agent,
    build_web_scraper_agent
)



def _parse_json_output(agent_output: Any, step: str) -> Dict[str, Any]:
    """Robust JSON parsing that handles direct JSON or JSON embedded in text."""
    text = getattr(agent_output, "output_text", None) or str(agent_output)
    
    # Try direct JSON parse first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # Try to extract JSON from text (with markdown code blocks)
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object in text
    match = re.search(r'\{.*\}', text, flags=re.DOTALL)
    if not match:
        # If no JSON found, print debug info and raise helpful error
        print(f"\n❌ Error parsing {step} output:")
        print(f"Raw output (first 500 chars):\n{text[:500]}")
        raise ValueError(f"{step} output is not JSON. Agent returned text instead of JSON object.")

    json_str = match.group(0)
    
    try:
        parsed = json.loads(json_str)
        if not isinstance(parsed, dict):
            raise ValueError(f"{step} output must be a JSON object, got {type(parsed)}")
        return parsed
    except json.JSONDecodeError as e:
        # Print debug information
        print(f"\n❌ JSON Parse Error in {step}:")
        print(f"Error: {e}")
        print(f"Problematic JSON (first 500 chars):\n{json_str[:500]}")
        print(f"\nAttempting to fix common JSON errors...")
        
        # Try to fix common JSON errors
        fixed_json = _try_fix_json(json_str)
        if fixed_json:
            try:
                parsed = json.loads(fixed_json)
                if isinstance(parsed, dict):
                    print(f"✅ Successfully fixed JSON!")
                    return parsed
            except:
                pass
        
        raise ValueError(f"{step} output has invalid JSON: {e}")


def _try_fix_json(json_str: str) -> Optional[str]:
    """Attempt to fix common JSON syntax errors."""
    try:
        # Fix trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing commas between fields (common AI mistake)
        json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
        
        # Fix single quotes to double quotes
        json_str = json_str.replace("'", '"')
        
        # Remove any trailing commas before closing braces
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json_str
    except:
        return None


async def _load_finance_with_entity(entity_agent: Any, guid: str, tools: MCPStdioTool) -> Dict[str, Any]:
    """Helper to load Finance object."""
    result = await entity_agent.run(
        f"guid={guid}\nOnly call finance_load(guid) and output the Finance JSON object.",
        tools=tools,
    )
    return _parse_json_output(result, "finance_load")


async def run_enhanced_financial_pipeline(
    user_prompt: str, 
    config: Optional[OrchestratorConfig] = None,
    fetch_comprehensive_data: bool = True,
    perform_analysis: bool = False
) -> Dict[str, Any]:
    """
    Enhanced orchestration pipeline with financial data extraction.
    
    Args:
        user_prompt: User's initial request
        config: Orchestrator configuration
        fetch_comprehensive_data: Whether to fetch comprehensive financial data
        perform_analysis: Whether to perform financial analysis
    """
    cfg = config or OrchestratorConfig()

    standard = build_chat_client("standard")
    fast = build_chat_client("fast")
    reasoning = build_chat_client("reasoning")

    # Use enhanced tools if available, fallback to original
    tools_path = Path(__file__).with_name("tools_enhanced.py")
    if not tools_path.exists():
        tools_path = Path(__file__).with_name(cfg.tools_file)
    
    if not tools_path.exists():
        raise FileNotFoundError(f"Missing MCP tools file: {tools_path}")

    async with MCPStdioTool(
        name="finance_tools",
        command=sys.executable,
        args=["-u", str(tools_path)],
        env=os.environ.copy(),
    ) as mcp_tools:
        async with (
            build_init_agent(standard) as init_agent,
            build_entity_agent(standard) as entity_agent,
            build_news_fetch_agent(fast) as news_agent,
            build_summary_sentiment_agent(reasoning) as sentiment_agent,
            build_inspector_agent(reasoning) as inspector_agent,
            build_orchestrator_agent(reasoning) as orchestrator_agent,
            build_financial_data_agent(reasoning) as financial_data_agent,
            build_financial_analysis_agent(reasoning) as analysis_agent,
            build_web_scraper_agent(fast) as scraper_agent,
        ):
            # Step 1: Initialize
            print("Step 1: Initializing Finance state...")
            init_raw = await init_agent.run(user_prompt, tools=mcp_tools)
            init_json = _parse_json_output(init_raw, "init")
            guid = init_json.get("guid")
            if not guid:
                raise ValueError(f"InitAgent did not return guid: {init_json}")
            print(f"Created GUID: {guid}")

            # Step 2: Core enrichment loop (original logic)
            print("\nStep 2: Running core enrichment pipeline...")
            last_step = "init"
            for iteration in range(cfg.max_loops):
                print(f"  Iteration {iteration + 1}/{cfg.max_loops}")
                finance = await _load_finance_with_entity(entity_agent, guid, mcp_tools)
                required_missing = [k for k in cfg.required_fields if not finance.get(k)]

                # Entity enrichment
                if any(field in required_missing for field in ("ticker", "description", "currency", "isin")):
                    print("    → Enriching entity data...")
                    await entity_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "entity"
                    continue

                assert cfg.articles_dir is not None, "articles_dir must be set"
                articles_file = cfg.articles_dir / f"{guid}_articles.json"

                # News fetching
                if not articles_file.exists():
                    print("    → Fetching news articles...")
                    await news_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "news"
                    continue

                # Sentiment analysis
                if not finance.get("News_Sentiment"):
                    print("    → Analyzing sentiment...")
                    await sentiment_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "sentiment"
                    continue

                # Quality inspection
                inspect_payload = {"finance": finance, "required": cfg.required_fields}
                inspect_raw = await inspector_agent.run(json.dumps(inspect_payload), tools=mcp_tools)
                inspect_json = _parse_json_output(inspect_raw, "inspector")

                # Orchestration decision
                orchestration_payload = {
                    "guid": guid, 
                    "inspector": inspect_json, 
                    "last_step": last_step
                }
                orchestration_raw = await orchestrator_agent.run(
                    json.dumps(orchestration_payload),
                    tools=mcp_tools,
                )
                decision = _parse_json_output(orchestration_raw, "orchestrator")

                next_step = decision.get("next_step", "final")
                if next_step == "final":
                    print("    → Core pipeline complete!")
                    break
                    
                # Execute next step
                if next_step == "entity":
                    await entity_agent.run(
                        f"guid={guid}\nNOTE:{inspect_json.get('suggested_fix', '')}",
                        tools=mcp_tools,
                    )
                    last_step = "entity"
                elif next_step == "news":
                    await news_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "news"
                elif next_step == "sentiment":
                    await sentiment_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "sentiment"
                else:
                    await entity_agent.run(f"guid={guid}", tools=mcp_tools)
                    last_step = "entity"

            # Step 3: Enhanced financial data extraction
            financial_data_summary = None
            if fetch_comprehensive_data:
                print("\nStep 3: Fetching comprehensive financial data...")
                finance = await _load_finance_with_entity(entity_agent, guid, mcp_tools)
                ticker = finance.get("ticker")
                
                if ticker:
                    financial_data_raw = await financial_data_agent.run(
                        f"guid={guid}\nFetch comprehensive financial data including: "
                        f"profile, financials, ratios, historical prices, analyst estimates, "
                        f"insider trading, institutional holdings, and SEC filings.",
                        tools=mcp_tools
                    )
                    financial_data_summary = _parse_json_output(financial_data_raw, "financial_data")
                    print(f"  Fetched {len(financial_data_summary.get('data_fetched', []))} data types")
                else:
                    print("  WARNING: No ticker available, skipping financial data fetch")

            # Step 4: Financial analysis
            analysis_summary = None
            if perform_analysis:
                print("\nStep 4: Performing financial analysis...")
                try:
                    analysis_raw = await analysis_agent.run(
                        f"guid={guid}\nPerform comprehensive financial analysis and generate "
                        f"investment recommendation based on all available data.",
                        tools=mcp_tools
                    )
                    analysis_summary = _parse_json_output(analysis_raw, "financial_analysis")
                    print(f"  Analysis complete - Recommendation: {analysis_summary.get('recommendation', 'N/A')}")
                except Exception as e:
                    print(f"  ⚠️ Analysis failed: {str(e)}")
                    print(f"  Continuing without investment analysis...")
                    analysis_summary = {
                        "error": str(e),
                        "message": "Financial analysis could not be completed. Data extraction was successful."
                    }

            # Step 5: Compile final results
            print("\nStep 5: Compiling final results...")
            finance_final = await _load_finance_with_entity(entity_agent, guid, mcp_tools)
            sentiment_raw = await sentiment_agent.run(f"guid={guid}", tools=mcp_tools)
            sentiment_json = _parse_json_output(sentiment_raw, "sentiment_final")

            result = {
                "guid": guid,
                "last_step": last_step,
                "finance": finance_final,
                "summary_sentiment": sentiment_json,
                "mcp_tools_file": str(tools_path),
            }

            if financial_data_summary:
                result["financial_data"] = financial_data_summary
            
            if analysis_summary:
                result["analysis"] = analysis_summary

            return result


async def main() -> None:
    """Main entry point - runs full comprehensive analysis."""
    print("=" * 80)
    print("  Enhanced Financial AI Agent - Comprehensive Analysis")
    print("=" * 80)
    
    # Get user input
    prompt = input("\nEnter company name or ticker: ").strip()
    
    if not prompt:
        print("❌ Error: Company name or ticker is required.")
        return
    
    print(f"\n🚀 Starting comprehensive analysis for: {prompt}")
    print("   - Fetching company data")
    print("   - Extracting financial information")
    print("   - Analyzing news sentiment")
    print("   - Generating investment recommendations")
    print("\n⏳ This may take 1-2 minutes...\n")
    
    try:
        # Run full analysis pipeline
        result = await run_enhanced_financial_pipeline(
            prompt,
            fetch_comprehensive_data=True,
            perform_analysis=True
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("  ANALYSIS COMPLETE")
        print("=" * 80)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("Please check your configuration and try again.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
