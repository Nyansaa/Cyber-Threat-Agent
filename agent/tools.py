# tools.py
# --------
# This file defines the tools that our agent can use.
# Right now we have one tool: web search.
# In Part 3, we'll add a RAG retrieval tool here as well.
#
# There are two parts to every tool:
#   1. The DEFINITION — tells Claude what the tool does and what inputs it needs
#   2. The FUNCTION — the actual Python code that runs when Claude calls the tool

from langchain_community.tools import DuckDuckGoSearchRun
from rag.retriever import search_documents

# ─── TOOL DEFINITIONS ─────────────────────────────────────────────────────────
# This is what we send to Claude via the API so it knows what tools are available.
# Claude reads these descriptions and decides when to use each tool.

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current cyber threat intelligence. "
            "Use this to find recent attack campaigns, CVEs, threat actor profiles, "
            "malware analysis reports, and security advisories. "
            "Always search before writing a threat brief."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query. Be specific — include threat name, "
                        "year, and context. Example: 'LockBit ransomware 2024 attack techniques TTPs'"
                    )
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_threat_intel_documents",
        "description": (
            "Search the internal threat intelligence document database. "
            "This database contains official cybersecurity advisories from agencies "
            "like CISA, FBI, NSA, and NCSC covering known threat actors, TTPs, IoCs, "
            "and mitigation guidance. ALWAYS search this database FIRST before using "
            "web_search — it contains authoritative, government-issued threat intel. "
            "Use web_search to supplement with recent news after consulting this database."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "The search query. Be specific — include threat actors, "
                        "TTPs, or sectors. Example: 'Iranian APT PLC critical infrastructure'"
                    )
                }
            },
            "required": ["query"]
        }
    }
]

# ─── TOOL FUNCTIONS ───────────────────────────────────────────────────────────
# This is the actual Python code that runs when Claude decides to use a tool.
# We initialize DuckDuckGo search once and reuse it for every query.

# Initialize the search tool (this runs once when the file is imported)
_search = DuckDuckGoSearchRun()

def web_search(query: str) -> str:
    """
    Run a web search using DuckDuckGo and return the results as a string.
    
    Args:
        query: The search query string
        
    Returns:
        A string containing the search results
    """
    print(f"\n  [🔍 Searching]: {query}")
    
    try:
        results = _search.run(query)
        print(f"  [✓ Got results]: {len(results)} characters returned")
        return results
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        print(f"  [✗ Search error]: {error_msg}")
        return error_msg


# ─── TOOL ROUTER ──────────────────────────────────────────────────────────────
# This function receives a tool name and its inputs from the agent loop
# and routes it to the correct Python function above.
# When we add more tools in Part 3, we'll add them here.

def run_tool(tool_name: str, tool_input: dict) -> str:
    """
    Route a tool call from Claude to the correct Python function.
    
    Args:
        tool_name: The name of the tool Claude wants to use
        tool_input: The inputs Claude is passing to the tool
        
    Returns:
        The result of the tool as a string
    """
    if tool_name == "web_search":
        return web_search(tool_input["query"])
    elif tool_name == "search_threat_intel_documents":
        return search_documents(tool_input["query"])
    else:
        return f"Unknown tool: {tool_name}"