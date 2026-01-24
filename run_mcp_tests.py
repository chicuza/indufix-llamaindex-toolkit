"""Run MCP integration tests with proper environment setup"""
import os
import sys

# Set environment variables from .env file
os.environ["LANGSMITH_API_KEY"] = "lsv2_pt_YOUR-KEY-HERE"
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"

# Import and run the validation script
import validate_integration

if __name__ == "__main__":
    exit(validate_integration.main())
