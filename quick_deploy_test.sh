#!/bin/bash
# Quick Deployment Test Script (Bash)
# Tests deployed LangGraph application endpoints and functionality

set -e

# Default values
DEPLOYMENT_URL="${1:-https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app}"
API_KEY="${ANTHROPIC_API_KEY:-}"
VERBOSE="${VERBOSE:-false}"

# Colors
COLOR_PASS="\033[0;32m"
COLOR_FAIL="\033[0;31m"
COLOR_WARN="\033[0;33m"
COLOR_INFO="\033[0;36m"
COLOR_RESET="\033[0m"

# Test counters
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Helper functions
print_header() {
    echo ""
    echo -e "${COLOR_INFO}======================================================================"
    echo -e "$1"
    echo -e "======================================================================${COLOR_RESET}"
}

print_test_result() {
    local test_name="$1"
    local passed="$2"
    local message="${3:-}"

    if [ "$passed" = "true" ]; then
        echo -e "${COLOR_PASS}[PASS]${COLOR_RESET} $test_name"
        ((PASS_COUNT++))
    else
        echo -e "${COLOR_FAIL}[FAIL]${COLOR_RESET} $test_name"
        ((FAIL_COUNT++))
    fi

    if [ -n "$message" ]; then
        echo "       $message"
    fi
}

print_warning() {
    local test_name="$1"
    local message="${2:-}"

    echo -e "${COLOR_WARN}[WARN]${COLOR_RESET} $test_name"
    if [ -n "$message" ]; then
        echo "       $message"
    fi
    ((WARN_COUNT++))
}

# Test functions
test_health_endpoint() {
    echo -e "\n${COLOR_INFO}Testing health endpoint...${COLOR_RESET}"

    local health_url="$DEPLOYMENT_URL/ok"
    local status_code

    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$health_url" --max-time 10)

    if [ "$status_code" = "200" ]; then
        print_test_result "Health Check" "true" "Endpoint is responsive"
        return 0
    else
        print_test_result "Health Check" "false" "Unexpected status code: $status_code"
        return 1
    fi
}

test_info_endpoint() {
    echo -e "\n${COLOR_INFO}Testing info endpoint...${COLOR_RESET}"

    local info_url="$DEPLOYMENT_URL/info"
    local response
    local status_code

    response=$(curl -s -w "\n%{http_code}" "$info_url" --max-time 10)
    status_code=$(echo "$response" | tail -n 1)

    if [ "$status_code" = "200" ]; then
        print_test_result "Info Endpoint" "true" "Retrieved deployment info"

        if [ "$VERBOSE" = "true" ]; then
            echo "       Info data:"
            echo "$response" | head -n -1 | python -m json.tool 2>/dev/null || echo "$response" | head -n -1
        fi

        return 0
    else
        print_test_result "Info Endpoint" "false" "Unexpected status code: $status_code"
        return 1
    fi
}

test_mcp_authentication() {
    echo -e "\n${COLOR_INFO}Testing MCP authentication...${COLOR_RESET}"

    if [ -z "$API_KEY" ]; then
        print_warning "MCP Authentication" "No API key provided - skipping auth test"
        return 2
    fi

    local invoke_url="$DEPLOYMENT_URL/runs/stream"
    local status_code

    local payload='{"input":{"messages":[{"role":"user","content":"Hello, what tools do you have?"}]},"config":{},"stream_mode":["values"]}'

    status_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$invoke_url" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "$payload" \
        --max-time 30)

    if [ "$status_code" = "200" ]; then
        print_test_result "MCP Authentication" "true" "Successfully authenticated and invoked"
        return 0
    elif [ "$status_code" = "401" ] || [ "$status_code" = "403" ]; then
        print_test_result "MCP Authentication" "false" "Authentication failed - check API key"
        return 1
    else
        print_test_result "MCP Authentication" "false" "Unexpected status code: $status_code"
        return 1
    fi
}

test_anthropic_api_key() {
    echo -e "\n${COLOR_INFO}Checking ANTHROPIC_API_KEY availability...${COLOR_RESET}"

    if [ -n "$ANTHROPIC_API_KEY" ]; then
        print_test_result "ANTHROPIC_API_KEY Environment Variable" "true" "Set in local environment"

        # Verify format (should start with sk-)
        if [[ "$ANTHROPIC_API_KEY" == sk-* ]]; then
            echo "       Key format appears valid"
        else
            print_warning "ANTHROPIC_API_KEY Format" "Key doesn't match expected format (should start with 'sk-')"
        fi

        return 0
    else
        print_test_result "ANTHROPIC_API_KEY Environment Variable" "false" "Not set in local environment"
        echo "       Note: This checks local env, not deployment env"
        return 1
    fi
}

test_deployment_secrets() {
    echo -e "\n${COLOR_INFO}Verifying GitHub Secrets configuration...${COLOR_RESET}"
    echo "       (This is informational - cannot verify directly)"

    echo ""
    echo "       Required GitHub Secrets:"
    echo "       - LANGSMITH_API_KEY"
    echo "       - WORKSPACE_ID"
    echo "       - INTEGRATION_ID"
    echo "       - LLAMA_CLOUD_API_KEY"
    echo "       - ANTHROPIC_API_KEY"

    echo ""
    echo "       Recommended GitHub Secrets:"
    echo "       - LANGCHAIN_TRACING_V2"
    echo "       - LANGCHAIN_PROJECT"
    echo "       - LANGCHAIN_ENDPOINT"

    print_warning "GitHub Secrets" "Verify these are set at: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions"
}

# Main execution
print_header "QUICK DEPLOYMENT TEST"
echo -e "${COLOR_INFO}Deployment URL: $DEPLOYMENT_URL${COLOR_RESET}"
echo -e "${COLOR_INFO}Timestamp: $(date '+%Y-%m-%d %H:%M:%S')${COLOR_RESET}"

# Run all tests
HEALTH_OK=false
INFO_OK=false
MCP_OK=false

test_health_endpoint && HEALTH_OK=true
test_info_endpoint && INFO_OK=true
test_mcp_authentication && MCP_OK=true || true  # Don't fail if skipped
test_anthropic_api_key || true
test_deployment_secrets

# Summary
print_header "TEST SUMMARY"
echo ""
echo -e "${COLOR_INFO}Results:${COLOR_RESET}"
echo -e "  Passed:  ${COLOR_PASS}$PASS_COUNT${COLOR_RESET}"
echo -e "  Failed:  ${COLOR_FAIL}$FAIL_COUNT${COLOR_RESET}"
echo -e "  Warnings: ${COLOR_WARN}$WARN_COUNT${COLOR_RESET}"
echo ""

# Overall status
if [ "$FAIL_COUNT" -eq 0 ] && [ "$HEALTH_OK" = "true" ] && [ "$INFO_OK" = "true" ]; then
    echo -e "OVERALL STATUS: ${COLOR_PASS}PASS${COLOR_RESET}"
    echo -e "${COLOR_PASS}Deployment is functioning correctly!${COLOR_RESET}"
    echo ""
    exit 0
elif [ "$HEALTH_OK" = "true" ] && [ "$INFO_OK" = "true" ]; then
    echo -e "OVERALL STATUS: ${COLOR_WARN}PARTIAL PASS${COLOR_RESET}"
    echo -e "${COLOR_WARN}Basic deployment is working, but some tests were skipped${COLOR_RESET}"
    echo ""
    exit 0
else
    echo -e "OVERALL STATUS: ${COLOR_FAIL}FAIL${COLOR_RESET}"
    echo -e "${COLOR_FAIL}Deployment has issues that need attention${COLOR_RESET}"
    echo ""
    exit 1
fi
