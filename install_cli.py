#!/usr/bin/env python3
"""Installation verification script for Indufix CLI Tools

Checks dependencies, verifies files, and guides initial setup.

Usage:
    python install_cli.py
"""

import sys
import os
import subprocess
from pathlib import Path


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_python_version():
    """Check Python version"""
    print_header("1. Python Version Check")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 11:
        print("[OK] Python version is 3.11+")
        return True
    else:
        print("[ERROR] Python 3.11+ required")
        print("Please upgrade Python")
        return False


def check_dependencies():
    """Check required dependencies"""
    print_header("2. Dependency Check")

    dependencies = {
        "requests": "HTTP client",
        "yaml": "YAML configuration (PyYAML)",
        "rich": "Terminal formatting (optional but recommended)"
    }

    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"[OK] {module:12} - {description}")
        except ImportError:
            if module == "rich":
                print(f"[WARN] {module:12} - {description} - OPTIONAL")
            else:
                print(f"[MISSING] {module:12} - {description}")
                all_ok = False

    if not all_ok:
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements-cli.txt")

    return all_ok


def check_cli_files():
    """Check CLI files exist"""
    print_header("3. CLI Files Check")

    required_files = [
        ("indufix_cli.py", "Master CLI"),
        ("setup_cli.py", "Setup wizard"),
        ("test_cli.py", "Testing interface"),
        ("deployment_cli.py", "Deployment management"),
        ("validate_cli.py", "Validation checks"),
        ("requirements-cli.txt", "CLI dependencies"),
        ("CLI_TOOLS_README.md", "Complete documentation"),
        ("QUICK_START_CLI.md", "Quick start guide")
    ]

    all_exist = True
    for filename, description in required_files:
        if Path(filename).exists():
            print(f"[OK] {filename:25} - {description}")
        else:
            print(f"[MISSING] {filename:25} - {description}")
            all_exist = False

    return all_exist


def check_environment():
    """Check environment variables"""
    print_header("4. Environment Variables Check")

    required_vars = {
        "LANGSMITH_API_KEY": "LangSmith API key (REQUIRED)",
        "LLAMA_CLOUD_API_KEY": "LlamaCloud API key (REQUIRED)",
        "ANTHROPIC_API_KEY": "Anthropic Claude API key (CRITICAL!)"
    }

    optional_vars = {
        "WORKSPACE_ID": "LangSmith workspace ID",
        "INTEGRATION_ID": "GitHub integration ID",
        "OPENAI_API_KEY": "OpenAI API key (optional)"
    }

    missing_required = []

    print("\nRequired:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"[OK] {var:25} - Set")
        else:
            print(f"[MISSING] {var:25} - {desc}")
            missing_required.append(var)

    print("\nOptional:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"[OK] {var:25} - Set")
        else:
            print(f"[NOT SET] {var:25} - {desc}")

    if missing_required:
        print("\nTo set environment variables:")
        print("\nWindows (PowerShell):")
        for var in missing_required:
            print(f'  $env:{var}="your-key-here"')
        print("\nWindows (CMD):")
        for var in missing_required:
            print(f'  set {var}=your-key-here')
        print("\nLinux/Mac:")
        for var in missing_required:
            print(f'  export {var}="your-key-here"')
        print("\nOr create .env file:")
        for var in missing_required:
            print(f'  echo "{var}=your-key-here" >> .env')

    return len(missing_required) == 0


def test_basic_functionality():
    """Test that CLIs can be imported"""
    print_header("5. Basic Functionality Test")

    tests = [
        ("indufix_cli.py", "IndufixCLI"),
        ("setup_cli.py", "SetupCLI"),
        ("test_cli.py", "TestSuite"),
        ("deployment_cli.py", "DeploymentCLI"),
        ("validate_cli.py", "ValidationCLI")
    ]

    all_ok = True
    for filename, class_name in tests:
        try:
            # Try to import the module
            module_name = filename.replace(".py", "")
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"[OK] {filename:25} - Can be imported")
            else:
                print(f"[WARN] {filename:25} - Class {class_name} not found")
        except Exception as e:
            print(f"[ERROR] {filename:25} - Import failed: {e}")
            all_ok = False

    return all_ok


def show_next_steps(all_checks_passed):
    """Show next steps"""
    print_header("Installation Summary")

    if all_checks_passed:
        print("\n[SUCCESS] All checks passed!")
        print("\nYour Indufix CLI tools are ready to use!")
        print("\nNext steps:")
        print("\n1. Verify installation:")
        print("   python indufix_cli.py status")
        print("\n2. Run setup wizard:")
        print("   python setup_cli.py")
        print("\n3. Validate everything:")
        print("   python validate_cli.py")
        print("\n4. Read the documentation:")
        print("   - Quick Start: QUICK_START_CLI.md")
        print("   - Full Docs: CLI_TOOLS_README.md")
        print("\n5. Get help:")
        print("   python indufix_cli.py help")
    else:
        print("\n[WARNING] Some checks failed!")
        print("\nPlease resolve the issues above before proceeding.")
        print("\nCommon fixes:")
        print("\n1. Install dependencies:")
        print("   pip install -r requirements-cli.txt")
        print("\n2. Set environment variables:")
        print("   See section 4 above for instructions")
        print("\n3. Verify all files are present:")
        print("   Check that all CLI files exist")

    print("\n" + "=" * 70)


def main():
    """Main installation verification"""
    print("=" * 70)
    print("  Indufix CLI Tools - Installation Verification")
    print("=" * 70)

    # Run all checks
    results = []
    results.append(check_python_version())
    results.append(check_dependencies())
    results.append(check_cli_files())
    results.append(check_environment())
    results.append(test_basic_functionality())

    # Show summary
    all_passed = all(results)
    show_next_steps(all_passed)

    # Return appropriate exit code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
