# core.py
# -------
# This is the brain of the Cyber Threat Intelligence Agent.
# It contains the main agentic loop — the back-and-forth between
# our code and Claude until Claude has finished its research
# and produced a structured threat brief.
#
# AGENTIC LOOP EXPLAINED:
#   1. We send Claude a threat topic
#   2. Claude decides to search the web (tool use)
#   3. We run the search and send results back to Claude
#   4. Claude may search again, or produce the final brief
#   5. We parse and return the brief
#   Steps 2-4 repeat until Claude is done — that's the "loop"

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOL_DEFINITIONS, run_tool

# ─── SETUP ────────────────────────────────────────────────────────────────────
# Load the API key from our .env file
# This is why we installed python-dotenv — it reads ANTHROPIC_API_KEY
# from the .env file so we never hardcode it in our code

load_dotenv()

# Initialize the Anthropic client — this is our connection to Claude
client = Anthropic()

# The Claude model we're using
MODEL = "claude-sonnet-4-6"


# ─── OUTPUT PARSER ────────────────────────────────────────────────────────────

def parse_brief(raw_text: str) -> dict:
    """
    Parse the JSON threat brief from Claude's response.
    
    Claude should return pure JSON, but sometimes it adds extra text.
    This function cleans it up and converts it to a Python dictionary.
    
    Args:
        raw_text: The raw text response from Claude
        
    Returns:
        A Python dictionary containing the threat brief
    """
    try:
        clean = raw_text.strip()
        # Find JSON content between curly braces
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end != 0:
            clean = clean[start:end]
        return json.loads(clean)
    except json.JSONDecodeError:
        print("  [⚠ Warning]: Could not parse JSON — returning raw output")
        return {"raw_output": raw_text}


# ─── DISPLAY BRIEF ────────────────────────────────────────────────────────────

def display_brief(brief: dict):
    """
    Pretty-print the threat brief to the terminal in a readable format.
    
    Args:
        brief: The parsed threat brief dictionary
    """
    # If parsing failed, just print the raw output
    if "raw_output" in brief:
        print("\n[RAW OUTPUT]\n")
        print(brief["raw_output"])
        return

    # Helper function to print a list section
    def list_section(label, items):
        print(f"\n  {label}")
        if items:
            for item in items:
                print(f"    • {item}")
        else:
            print("    • N/A")

    print("\n" + "=" * 65)
    print("       CYBER THREAT INTELLIGENCE BRIEF")
    print("=" * 65)
    print(f"\n  THREAT:     {brief.get('threat_name', 'N/A')}")
    print(f"  TYPE:       {brief.get('threat_type', 'N/A')}")
    print(f"  SEVERITY:   {brief.get('severity', 'N/A')}")
    print(f"  CONFIDENCE: {brief.get('confidence', 'N/A')}")
    print(f"\n  SUMMARY\n  {brief.get('summary', 'N/A')}")

    list_section("THREAT ACTORS",              brief.get("threat_actors", []))
    list_section("TARGETED SECTORS",           brief.get("targeted_sectors", []))
    list_section("ATTACK VECTORS",             brief.get("attack_vectors", []))
    list_section("INDICATORS OF COMPROMISE",   brief.get("indicators_of_compromise", []))
    list_section("MITIGATIONS",                brief.get("mitigations", []))

    print("\n" + "=" * 65 + "\n")


# ─── SAVE BRIEF ───────────────────────────────────────────────────────────────

def save_brief(brief: dict, threat_topic: str):
    """
    Save the threat brief as a JSON file in the briefs/ folder.
    
    Args:
        brief: The parsed threat brief dictionary
        threat_topic: The original topic (used for the filename)
    """
    # Create a safe filename from the threat topic
    safe_name = threat_topic[:40].replace(" ", "_").replace("/", "-")
    filename = f"briefs/brief_{safe_name}.json"
    
    with open(filename, "w") as f:
        json.dump(brief, f, indent=2)
    
    print(f"  [💾 Saved]: {filename}\n")


# ─── MAIN AGENT LOOP ──────────────────────────────────────────────────────────

def run_agent(threat_topic: str) -> dict:
    """
    The main agentic loop. This function:
      1. Sends the threat topic to Claude
      2. Handles tool calls (web search) in a loop
      3. Returns the final structured threat brief
    
    Args:
        threat_topic: The cyber threat to research (e.g. "LockBit ransomware")
        
    Returns:
        A dictionary containing the structured threat brief
    """
    print(f"\n[🤖 Agent] Starting research on: {threat_topic}")
    print("-" * 65)

    # Start the conversation with the user's threat topic
    messages = [
        {
            "role": "user",
            "content": (
                f"Research this cyber threat and produce a structured threat brief:\n\n"
                f"THREAT TOPIC: {threat_topic}\n\n"
                f"Search the web for current intelligence on this threat before "
                f"generating the brief. Focus on information relevant to "
                f"defense, government, and critical infrastructure sectors."
            )
        }
    ]

    # ── AGENTIC LOOP ──────────────────────────────────────────────────────────
    # This loop keeps running until Claude stops using tools and gives us
    # the final threat brief. Each iteration is one "turn" in the conversation.

    iteration = 0
    max_iterations = 10  # Safety limit to prevent infinite loops

    while iteration < max_iterations:
        iteration += 1
        print(f"\n[Agent Turn {iteration}]")

        # Send the current conversation to Claude
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        # Add Claude's response to our conversation history
        # This is important — Claude needs to see its own previous responses
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # ── CHECK WHAT CLAUDE DECIDED TO DO ───────────────────────────────────

        if response.stop_reason == "end_turn":
            # Claude is done — extract and return the final text response
            print("\n[✓ Agent] Research complete. Generating brief...")
            
            for block in response.content:
                if hasattr(block, "text"):
                    return parse_brief(block.text)
            
            # If no text block found, something went wrong
            return {"raw_output": "No text response found in final message."}

        elif response.stop_reason == "tool_use":
            # Claude wants to use a tool — process all tool calls in this response
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"  [🔧 Tool call]: {block.name}")
                    
                    # Run the tool and get the result
                    result = run_tool(block.name, block.input)
                    
                    # Package the result to send back to Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Send the tool results back to Claude so it can continue
            messages.append({
                "role": "user",
                "content": tool_results
            })

        else:
            # Unexpected stop reason — exit the loop
            print(f"[⚠ Unexpected stop reason]: {response.stop_reason}")
            break

    # If we hit the max iterations limit
    return {"raw_output": "Agent reached maximum iterations without completing."}


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    """
    Main entry point for the CTI Agent.
    Runs an interactive loop where the user can enter threat topics.
    """
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║        Cyber Threat Intelligence Agent v0.1             ║")
    print("║        Built for defense & intelligence analysts        ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # Check that the API key is loaded
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY not found.")
        print("  Make sure your .env file exists and contains your key.")
        print("  Example: ANTHROPIC_API_KEY=sk-ant-api03-...")
        return

    print("Type a cyber threat topic to research.")
    print("Examples: 'LockBit ransomware', 'APT29 techniques', 'Log4Shell exploit'\n")

    # Interactive loop — keep asking for topics until the user quits
    while True:
        threat_topic = input("Enter threat topic (or 'quit' to exit):\n> ").strip()

        if threat_topic.lower() in ("quit", "exit", "q"):
            print("\nExiting. Stay secure! 🔒")
            break

        if not threat_topic:
            print("Please enter a threat topic.\n")
            continue

        # Run the agent and get the brief
        brief = run_agent(threat_topic)
        
        # Display the brief in the terminal
        display_brief(brief)

        # Ask if they want to save it
        save = input("Save this brief to file? (y/n): ").strip().lower()
        if save == "y":
            save_brief(brief, threat_topic)