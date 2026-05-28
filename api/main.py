# api/main.py
# -----------
# This file turns the CTI Agent into a REST API web service.
# Instead of running in the terminal, users can send HTTP requests
# to get threat briefs back as JSON responses.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from agent.core import run_agent
# ─── APP INITIALIZATION ───────────────────────────────────────────────────────

app = FastAPI(
    title="Cyber Threat Intelligence Agent API",
    description=(
        "Agentic AI system that researches cyber threats and produces "
        "structured analyst briefs. Combines RAG over internal threat intel "
        "documents with real-time web search."
    ),
    version="1.0.0"
)

# Enable CORS so browsers from any domain can call this API
# In production you'd restrict this to specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REQUEST & RESPONSE MODELS ────────────────────────────────────────────────
# Pydantic models define the shape of data going IN and OUT of the API.
# This gives us automatic validation — if someone sends bad data, FastAPI
# returns a clear error instead of crashing.

class ResearchRequest(BaseModel):
    """The input from the user — what threat they want researched."""
    threat_topic: str = Field(
        ...,
        description="The cyber threat to research",
        examples=["LockBit ransomware", "APT29 phishing techniques"]
    )

class ThreatBrief(BaseModel):
    """The structured threat brief returned by the agent."""
    threat_name: Optional[str] = None
    threat_type: Optional[str] = None
    summary: Optional[str] = None
    threat_actors: Optional[list] = None
    targeted_sectors: Optional[list] = None
    attack_vectors: Optional[list] = None
    indicators_of_compromise: Optional[list] = None
    mitigations: Optional[list] = None
    severity: Optional[str] = None
    confidence: Optional[str] = None
    raw_output: Optional[str] = None  # fallback if JSON parsing fails
    # ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint — confirms the API is running."""
    return {
        "service": "Cyber Threat Intelligence Agent",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "research": "POST /research — Submit a threat topic for analysis",
            "docs": "GET /docs — Interactive API documentation",
            "health": "GET /health — Service health check"
        }
    }


@app.get("/health")
def health_check():
    """Simple health check for monitoring tools."""
    return {"status": "healthy"}


@app.post("/research", response_model=ThreatBrief)
def research_threat(request: ResearchRequest):
    """
    Submit a cyber threat topic for autonomous research.
    
    The agent will:
    1. Search the internal threat intelligence database (RAG)
    2. Supplement with current web search results
    3. Synthesize findings into a structured threat brief
    
    Example request:
        POST /research
        { "threat_topic": "Iranian APT targeting critical infrastructure" }
    """
    try:
        # Call your existing agent — no changes needed!
        brief = run_agent(request.threat_topic)
        
        # Return the brief — FastAPI converts it to JSON automatically
        return brief
        
    except Exception as e:
        # If something goes wrong, return a clean HTTP error
        raise HTTPException(
            status_code=500,
            detail=f"Agent research failed: {str(e)}"
        )
        # ─── RUN THE SERVER ───────────────────────────────────────────────────────────
# This lets you start the API by running: python -m api.main
# In production you'd use a process manager like systemd or Docker instead.

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",  # Accept connections from any IP
        port=8000,
        reload=True       # Auto-restart when you edit code (dev mode)
    )
    
        