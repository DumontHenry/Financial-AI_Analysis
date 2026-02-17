#!/usr/bin/env python3
"""
Enhanced Financial AI Agent System - Complete Setup & Verification
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_section(text: str) -> None:
    """Print section header."""
    print(f"\n📋 {text}")

def check_python_version() -> bool:
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    meets_requirement = version >= (3, 10)
    
    if meets_requirement:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.10+)")
    
    return meets_requirement

def check_file(filename: str, required: bool = True) -> bool:
    """Check if a file exists."""
    exists = Path(filename).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "REQUIRED" if required else "Optional"
    print(f"{status} {filename:40s} [{req_text}]")
    return exists

def check_files() -> Tuple[int, int, int]:
    """Check all required and optional files."""
    print_section("File Verification")
    
    required_files = [
        "agent_dependencies.py",
        "chat_client_factory.py",
        "tools_enhanced.py",
        "financial_agents.py",
        "magentic_agent_enhanced.py",
        "init_agent.py",
        "entity_agent.py",
        "fetch_news.py",
        "sentiment_agent.py",
        "inspector_agent.py",
        "orchestrator_decision_agent.py",
    ]
    
    optional_files = [
        ".env",
        "tools.py",
        "requirements.txt",
    ]
    
    required_found = sum(check_file(f, required=True) for f in required_files)
    optional_found = sum(check_file(f, required=False) for f in optional_files)
    
    return required_found, len(required_files), optional_found

def check_dependencies() -> Tuple[List[str], List[str]]:
    """Check if required Python packages are installed."""
    print_section("Python Dependencies")
    
    packages = {
        "agent_framework": "agent-framework",
        "requests": "requests",
        "dotenv": "python-dotenv",
        "fastmcp": "fastmcp",
        "pydantic": "pydantic",
    }
    
    installed = []
    missing = []
    
    for module_name, package_name in packages.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
            installed.append(package_name)
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    return installed, missing

def check_env_file() -> Tuple[List[str], List[str]]:
    """Check .env file configuration."""
    print_section("Environment Configuration")
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
        "FMP_API_KEY",
    ]
    
    optional_vars = [
        "AZURE_OPENAI_FAST_DEPLOYMENT",
        "AZURE_OPENAI_REASONING_DEPLOYMENT",
        "FINANCE_STATE_DIR",
        "FINANCE_ARTICLES_DIR",
        "FINANCIAL_DATA_DIR",
    ]
    
    if not Path(".env").exists():
        print("❌ .env file not found")
        print("\n💡 Create .env file from .env.example:")
        print("   cp .env.example .env")
        return [], required_vars
    
    from dotenv import load_dotenv
    load_dotenv()
    
    configured = []
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value and value.strip():
            print(f"✅ {var}")
            configured.append(var)
        else:
            print(f"❌ {var}")
            missing.append(var)
    
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and value.strip():
            print(f"✅ {var} = {value}")
        else:
            print(f"⚠️  {var} (using default)")
    
    return configured, missing

def check_directories() -> None:
    """Check and create storage directories."""
    print_section("Storage Directories")
    
    dirs = {
        "agent_state": "Finance state objects",
        "agent_articles": "News articles",
        "financial_data": "Financial data cache",
    }
    
    for dir_name, description in dirs.items():
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name:20s} - {description}")
        else:
            print(f"⚠️  {dir_name:20s} - Creating...")
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {dir_path.absolute()}")

def test_imports() -> bool:
    """Test if all modules can be imported."""
    print_section("Module Import Test")
    
    modules = [
        "agent_dependencies",
        "chat_client_factory",
        "tools_enhanced",
        "financial_agents",
        "init_agent",
        "entity_agent",
        "fetch_news",
        "sentiment_agent",
        "inspector_agent",
        "orchestrator_decision_agent",
    ]
    
    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {str(e)}")
            success = False
    
    return success

def print_summary(
    python_ok: bool,
    files_found: int,
    files_required: int,
    deps_installed: List[str],
    deps_missing: List[str],
    env_configured: List[str],
    env_missing: List[str],
) -> None:
    """Print setup summary."""
    print_header("Setup Summary")
    
    total_checks = 4
    passed_checks = 0
    
    # Python version
    if python_ok:
        print("✅ Python Version: Compatible")
        passed_checks += 1
    else:
        print("❌ Python Version: Upgrade to 3.10+")
    
    # Files
    if files_found == files_required:
        print(f"✅ Files: All required files present ({files_found}/{files_required})")
        passed_checks += 1
    else:
        print(f"❌ Files: Missing {files_required - files_found} required files")
    
    # Dependencies
    if not deps_missing:
        print(f"✅ Dependencies: All installed ({len(deps_installed)})")
        passed_checks += 1
    else:
        print(f"❌ Dependencies: {len(deps_missing)} missing")
    
    # Environment
    if not env_missing:
        print(f"✅ Environment: Fully configured")
        passed_checks += 1
    else:
        print(f"❌ Environment: {len(env_missing)} variables missing")
    
    print(f"\n📊 Score: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("\n🎉 Setup Complete! Ready to run the financial agent system.")
    else:
        print("\n⚠️  Setup Incomplete. Follow instructions below.")

def print_next_steps(
    deps_missing: List[str],
    env_missing: List[str],
) -> None:
    """Print next steps for incomplete setup."""
    print_header("Next Steps")
    
    if deps_missing:
        print("\n1️⃣  Install Missing Dependencies:")
        print("   pip install -r requirements.txt")
        print("\n   Or install individually:")
        for pkg in deps_missing:
            print(f"   pip install {pkg}")
    
    if env_missing:
        print("\n2️⃣  Configure Environment:")
        print("   a) Copy example config:")
        print("      cp .env.example .env")
        print("\n   b) Edit .env and add your API keys:")
        print("      nano .env")
        print("\n   Required keys:")
        for var in env_missing:
            print(f"      - {var}")
        print("\n   Get API keys:")
        print("      - Azure OpenAI: https://portal.azure.com")
        print("      - FMP API: https://financialmodelingprep.com/developer/docs/")
    
    print("\n3️⃣  Test the Setup:")
    print("   python magentic_agent_enhanced.py")
    
    print("\n4️⃣  Read Documentation:")
    print("   - README.md - Project overview")
    print("   - QUICKSTART_GUIDE.md - Usage examples")
    print("   - AZURE_MODEL_GUIDE.md - Model selection")
    print("   - ENHANCED_SYSTEM_DOCUMENTATION.md - Full docs")

def main() -> None:
    """Main setup verification."""
    print_header("Enhanced Financial AI Agent System - Setup Verification")
    
    # Check Python version
    print_section("Python Version")
    python_ok = check_python_version()
    
    # Check files
    files_found, files_required, optional_found = check_files()
    
    # Check dependencies
    try:
        deps_installed, deps_missing = check_dependencies()
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        deps_installed, deps_missing = [], []
    
    # Check environment
    try:
        env_configured, env_missing = check_env_file()
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        env_configured, env_missing = [], []
    
    # Check directories
    try:
        check_directories()
    except Exception as e:
        print(f"❌ Error with directories: {e}")
    
    # Test imports
    if not deps_missing:
        try:
            test_imports()
        except Exception as e:
            print(f"❌ Import test failed: {e}")
    
    # Print summary
    print_summary(
        python_ok,
        files_found,
        files_required,
        deps_installed,
        deps_missing,
        env_configured,
        env_missing,
    )
    
    # Print next steps if setup is incomplete
    if deps_missing or env_missing or files_found < files_required:
        print_next_steps(deps_missing, env_missing)
    else:
        print("\n🚀 Quick Start:")
        print("   python magentic_agent_enhanced.py")

if __name__ == "__main__":
    main()
