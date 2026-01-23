@echo off
REM Setup script for MCP CLI testing on Windows
REM Official method for configuring MCP test environment

echo ========================================
echo MCP CLI Test Environment Setup
echo ========================================
echo.

REM Prompt for LangSmith API Key
set /p LANGSMITH_API_KEY="Enter your LangSmith API Key: "

REM Set workspace ID (default provided)
set LANGSMITH_WORKSPACE_ID=950d802b-125a-45bc-88e4-3d7d0edee182

REM Set deployment URL (default provided)
set MCP_DEPLOYMENT_URL=https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app

echo.
echo ========================================
echo Environment Variables Set
echo ========================================
echo LANGSMITH_API_KEY: %LANGSMITH_API_KEY:~0,20%...
echo LANGSMITH_WORKSPACE_ID: %LANGSMITH_WORKSPACE_ID%
echo MCP_DEPLOYMENT_URL: %MCP_DEPLOYMENT_URL%
echo.

REM Run the test
echo ========================================
echo Running MCP CLI Test
echo ========================================
echo.

python test_mcp_cli.py

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
pause
