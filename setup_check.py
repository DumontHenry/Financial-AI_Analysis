"""
Setup Verification Script
Checks that all requirements are met before running the financial agent system
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    major = sys.version_info.major
    minor = sys.version_info.minor
    
    if major >= 3 and minor >= 10:
        print_success(f"Python {major}.{minor} detected (Required: 3.10+)")
        return True
    else:
        print_error(f"Python {major}.{minor} detected (Required: 3.10+)")
        print(f"  Please upgrade Python to 3.10 or higher")
        return False

def check_dependencies():
    """Check required Python packages"""
    print_header("Checking Dependencies")
    
    required_packages = [
        "agent_framework",
        "requests",
        "pydantic",
        "dotenv",
        "fastmcp"
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            all_installed = False
    
    if not all_installed:
        print(f"\n  Install missing packages:")
        print(f"  pip install -r requirements.txt")
    
    return all_installed

def check_env_file():
    """Check .env file exists"""
    print_header("Checking Configuration Files")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print_success(".env file exists")
        return True
    else:
        print_error(".env file NOT found")
        print(f"  Create .env file from .env.example:")
        print(f"  cp .env.example .env")
        print(f"  Then edit .env with your API keys")
        return False

def check_env_variables():
    """Check required environment variables"""
    print_header("Checking Environment Variables")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint URL",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "Standard model deployment",
        "FMP_API_KEY": "Financial Modeling Prep API key"
    }
    
    optional_vars = {
        "AZURE_OPENAI_FAST_DEPLOYMENT": "Fast model deployment",
        "AZURE_OPENAI_REASONING_DEPLOYMENT": "Reasoning model deployment"
    }
    
    all_set = True
    
    print("\nRequired variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "your-key-here" and value != "your-resource-name":
            print_success(f"{var} is set")
        else:
            print_error(f"{var} is NOT set")
            print(f"  {description}")
            all_set = False
    
    print("\nOptional variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != "your-key-here":
            print_success(f"{var} is set")
        else:
            print_warning(f"{var} not set (will use default)")
    
    return all_set

def check_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print_header("Testing Azure OpenAI Connection")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Try to list models (lightweight test)
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        print_success(f"Successfully connected to Azure OpenAI")
        print_success(f"Model '{deployment}' is accessible")
        return True
        
    except Exception as e:
        print_error(f"Failed to connect to Azure OpenAI")
        print(f"  Error: {str(e)}")
        print(f"  Check your AZURE_OPENAI_* environment variables")
        return False

def check_fmp_api():
    """Test FMP API connection"""
    print_header("Testing FMP API Connection")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("FMP_API_KEY")
    
    if not api_key or api_key == "your-fmp-api-key-here":
        print_error("FMP API key not configured")
        return False
    
    try:
        import requests
        
        url = "https://financialmodelingprep.com/stable/quote"
        params = {"symbol": "AAPL", "apikey": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("Successfully connected to FMP API")
            print_success("API key is valid")
            return True
        else:
            print_error(f"FMP API returned error: {response.status_code}")
            print(f"  Check your FMP_API_KEY")
            return False
            
    except Exception as e:
        print_error(f"Failed to connect to FMP API")
        print(f"  Error: {str(e)}")
        return False

def check_files():
    """Check required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        "tools_enhanced.py",
        "financial_agents.py",
        "magentic_agent_enhanced.py",
        "requirements.txt",
        ".env.example"
    ]
    
    all_exist = True
    
    for filename in required_files:
        if Path(filename).exists():
            print_success(f"{filename} exists")
        else:
            print_error(f"{filename} NOT found")
            all_exist = False
    
    return all_exist

def check_directories():
    """Check/create storage directories"""
    print_header("Checking Storage Directories")
    
    directories = [
        "agent_state",
        "agent_articles", 
        "financial_data"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print_success(f"{dir_name}/ exists")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"{dir_name}/ created")
            except Exception as e:
                print_error(f"Failed to create {dir_name}/")
                print(f"  Error: {str(e)}")
                return False
    
    return True

def main():
    """Run all checks"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Financial AI Agent - Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration File", check_env_file),
        ("Environment Variables", check_env_variables),
        ("Required Files", check_files),
        ("Storage Directories", check_directories),
        ("Azure OpenAI Connection", check_azure_openai_connection),
        ("FMP API Connection", check_fmp_api),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error running {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {name:.<40} {status}")
    
    print(f"\n  Checks passed: {passed}/{total}")
    
    if passed == total:
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}  ✓ All checks passed! You're ready to go!{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"\n  Next step: Run the main program")
        print(f"  python magentic_agent_enhanced.py")
        return 0
    else:
        print(f"\n{RED}{'='*60}{RESET}")
        print(f"{RED}  ✗ Some checks failed. Please fix the issues above.{RESET}")
        print(f"{RED}{'='*60}{RESET}")
        print(f"\n  Need help? Check the documentation:")
        print(f"  - QUICKSTART_GUIDE.md")
        print(f"  - AZURE_MODEL_GUIDE.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
