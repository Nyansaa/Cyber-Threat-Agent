# __init__.py
# -----------
# This file tells Python that the "agent" folder is a package —
# meaning other files can import from it using "from agent.core import..."
#
# It also exposes the main functions so they're easy to import
# from outside the agent folder.

from agent.core import run_agent, display_brief, save_brief, main