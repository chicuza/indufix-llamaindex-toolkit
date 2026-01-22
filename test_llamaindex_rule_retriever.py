"""Test LlamaIndex_Rule_Retriever Subagent Integration with indufix_agent Tool"""
import requests
import json
import time
from datetime import datetime

# Configuration
AGENT_ID = "1bf73a52-638f-4c42-8fc7-d6d07405c4fe"
WORKSPACE_ID = "950d802b-125a-45bc-88e4-3d7d0edee182"
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
LANGSMITH_API_BASE = "https://api.smith.langchain.com"
DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"

def get_headers():
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

print("=" * 70)
print("LLAMAINDEX RULE RETRIEVER SUBAGENT TEST")
print("=" * 70)
print(f"\nAgent ID: {AGENT_ID}")
print(f"Workspace ID: {WORKSPACE_ID}")
print(f"Deployment: {DEPLOYMENT_URL}")
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test 1: Verify MCP Server is Accessible
print("\n" + "=" * 70)
print("[Test 1] MCP Server Accessibility")
print("=" * 70)

try:
    response = requests.get(f"{DEPLOYMENT_URL}/ok", timeout=10)
    if response.status_code == 200:
        print("[OK] MCP server is online and accessible")
        mcp_accessible = True
    else:
        print(f"[WARNING] MCP server status: {response.status_code}")
        mcp_accessible = False
except Exception as e:
    print(f"[ERROR] Cannot reach MCP server: {e}")
    mcp_accessible = False

# Test 2: Verify indufix_agent Tool via MCP
print("\n" + "=" * 70)
print("[Test 2] MCP Tool Discovery")
print("=" * 70)

if mcp_accessible:
    try:
        headers = get_headers()
        headers["Accept"] = "application/json"

        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=mcp_request,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"[OK] Found {len(tools)} tool(s) via MCP")
                for tool in tools:
                    print(f"  - {tool.get('name')}")
                tool_available = True
            else:
                print("[ERROR] Unexpected MCP response structure")
                tool_available = False
        else:
            print(f"[ERROR] MCP status: {response.status_code}")
            tool_available = False

    except Exception as e:
        print(f"[ERROR] MCP tool discovery failed: {e}")
        tool_available = False
else:
    tool_available = False
    print("[SKIPPED] MCP server not accessible")

# Test 3: Test Direct Tool Invocation
print("\n" + "=" * 70)
print("[Test 3] Direct Tool Invocation Test")
print("=" * 70)

if tool_available:
    test_queries = [
        {
            "name": "Default Values",
            "query": "Busque valores default para parafuso M10",
            "expected": "Should retrieve default values for M10 bolts"
        },
        {
            "name": "Standard Equivalence",
            "query": "Equivalência entre DIN 933 e ISO 4017",
            "expected": "Should find standard equivalences"
        },
        {
            "name": "Rule Retrieval",
            "query": "Regras para parafuso sextavado",
            "expected": "Should retrieve hex bolt rules"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n[Test 3.{i}] {test['name']}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")

        try:
            headers = get_headers()
            headers["Accept"] = "application/json"

            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "indufix_agent",
                    "arguments": {
                        "messages": [
                            {
                                "role": "user",
                                "content": test['query']
                            }
                        ]
                    }
                },
                "id": i + 10
            }

            response = requests.post(
                f"{DEPLOYMENT_URL}/mcp",
                json=call_request,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"[OK] Tool invoked successfully")

                # Save response for analysis
                filename = f"test_3_{i}_{test['name'].replace(' ', '_')}.json"
                with open(filename, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"[INFO] Response saved to: {filename}")

            else:
                print(f"[ERROR] Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"[ERROR] Tool invocation failed: {e}")

        time.sleep(1)  # Rate limiting

else:
    print("[SKIPPED] Tool not available")

# Test 4: Integration Instructions
print("\n" + "=" * 70)
print("[Test 4] Subagent Integration Status")
print("=" * 70)

print("\n[CONFIGURATION REQUIRED]")
print("To complete integration, perform these steps in Agent Builder UI:")

print("\nStep 1: Add MCP Server to Workspace")
print("  - Navigate to: Settings -> Workspace -> MCP Servers")
print("  - If 'indufix-llamaindex-toolkit' is not listed, add it:")
print(f"    Name: indufix-llamaindex-toolkit")
print(f"    URL: {DEPLOYMENT_URL}/mcp")
print("    Auth: Use workspace authentication")

print("\nStep 2: Configure LlamaIndex_Rule_Retriever Subagent")
print(f"  - Open agent editor: https://smith.langchain.com/o/{WORKSPACE_ID}/agents/editor?agentId={AGENT_ID}")
print("  - Locate: LlamaIndex_Rule_Retriever subagent")
print("  - Add tool: indufix_agent")

print("\nStep 3: Update Subagent System Prompt")
print("  Add to LlamaIndex_Rule_Retriever prompt:")
print('''
  """
  You have access to the indufix_agent tool with 6 capabilities:

  1. retrieve_matching_rules - Vector retrieval from knowledge base
  2. query_indufix_knowledge - Query engine with synthesis
  3. get_default_values - Default values for missing attributes
  4. get_standard_equivalences - Standard equivalences (DIN/ISO/ASTM)
  5. get_confidence_penalty - Confidence penalties for inferred values
  6. pipeline_retrieve_raw - Direct pipeline access (debug)

  Use this tool when retrieving rules, specifications, defaults, or
  equivalences from the Forjador Indufix knowledge base.
  """
''')

print("\nStep 4: Test in Agent Builder")
print("  - Open agent chat interface")
print("  - Send queries that should trigger LlamaIndex_Rule_Retriever")
print("  - Verify subagent uses indufix_agent tool")
print("  - Check response quality")

# Test 5: Recommended Test Queries for Agent
print("\n" + "=" * 70)
print("[Test 5] Recommended Agent Test Queries")
print("=" * 70)

print("\nAfter configuration, test with these queries in Agent Builder:")

agent_test_queries = [
    {
        "query": "Busque regras para parafuso M10",
        "triggers": "LlamaIndex_Rule_Retriever",
        "expected": "Subagent retrieves M10 bolt rules"
    },
    {
        "query": "Valores default para parafuso sextavado",
        "triggers": "LlamaIndex_Rule_Retriever -> get_default_values",
        "expected": "Default values for hex bolts"
    },
    {
        "query": "Equivalência entre DIN 933 e ISO 4017",
        "triggers": "LlamaIndex_Rule_Retriever -> get_standard_equivalences",
        "expected": "Standard equivalence information"
    },
    {
        "query": "Penalidade de confiança para material inferido por LLM",
        "triggers": "LlamaIndex_Rule_Retriever -> get_confidence_penalty",
        "expected": "Confidence penalty values"
    },
    {
        "query": "Especificações técnicas de parafuso classe 8.8",
        "triggers": "LlamaIndex_Rule_Retriever -> query_indufix_knowledge",
        "expected": "Technical specifications with synthesis"
    }
]

for i, test in enumerate(agent_test_queries, 1):
    print(f"\n{i}. {test['query']}")
    print(f"   Should trigger: {test['triggers']}")
    print(f"   Expected result: {test['expected']}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

results = []
results.append(("MCP Server Accessible", mcp_accessible))
results.append(("Tool Available via MCP", tool_available))

print("\n[RESULTS]")
for test_name, result in results:
    status = "[OK]" if result else "[FAILED]"
    print(f"{status} {test_name}")

passed = sum(1 for _, r in results if r)
total = len(results)
print(f"\nAutomated Tests: {passed}/{total} passed")

print("\n[NEXT STEPS]")
if passed == total:
    print("1. Complete UI configuration (Steps 1-3 above)")
    print("2. Test subagent in Agent Builder")
    print("3. Verify tool usage with recommended queries")
    print("4. Document results")
else:
    print("1. Fix failed tests before proceeding")
    print("2. Verify MCP server status")
    print("3. Check deployment logs")

print("\n[DOCUMENTATION]")
print("See: LLAMAINDEX_RULE_RETRIEVER_INTEGRATION.md (to be created)")
print("See: AGENT_INTEGRATION_FINDINGS.md (existing)")

print("\n" + "=" * 70)
print("END OF TEST")
print("=" * 70)
