# 🛡️ Cyber Threat Intelligence (CTI) Agent

An **agentic AI system** that autonomously researches cyber threats and produces structured, analyst-ready threat briefs for defense and intelligence applications.

Combines **RAG over official threat intelligence documents** (CISA, FBI, NSA, NCSC advisories) with **real-time web search** to deliver authoritative, current threat analysis — exposed via a production-ready **REST API**.

---

## 📌 Overview

The CTI Agent accepts a cyber threat topic and autonomously:

1. **Searches an internal knowledge base** of official cybersecurity advisories using RAG (ChromaDB + sentence-transformers embeddings)
2. **Supplements with real-time web search** for recent campaigns and emerging threats
3. **Synthesizes findings** into a structured JSON threat brief covering threat actors, TTPs, IoCs, targeted sectors, and recommended mitigations
4. **Delivers results via a REST API** that can integrate with any downstream system

This project demonstrates applied agentic AI in a defense and intelligence context — combining large language model reasoning, retrieval-augmented generation, and real-time research to automate analyst workflows.

---

## 🎯 Use Case

Defense contractors, government agencies, and intelligence community analysts spend significant time manually researching threats and writing briefs. This agent automates that pipeline — producing a structured analyst-grade brief in under a minute, grounded in authoritative government advisories.

**Example request:**
\`\`\`json
POST /research
{
  "threat_topic": "Iranian APT targeting PLCs in US critical infrastructure"
}
\`\`\`

**Example response (abridged):**
\`\`\`json
{
  "threat_name": "Iranian APT / CyberAv3ngers - PLC Exploitation Across U.S. Critical Infrastructure",
  "threat_type": "APT / ICS-OT Attack / Critical Infrastructure Sabotage",
  "summary": "Iran-affiliated APT actors, including the IRGC Cyber-Electronic Command-linked group CyberAv3ngers, are actively targeting internet-exposed PLCs across multiple U.S. critical infrastructure sectors...",
  "threat_actors": ["CyberAv3ngers (IRGC)", "Iranian-affiliated APT", "IRGC"],
  "targeted_sectors": ["Water and Wastewater Systems", "Energy", "Defense Industrial Base", "Government"],
  "attack_vectors": ["Direct exploitation of internet-exposed PLCs", "Malicious modification of PLC project files", "Manipulation of HMI/SCADA data"],
  "mitigations": ["Remove PLCs from direct internet exposure", "Implement multi-factor authentication", "Network segmentation for OT environments"],
  "severity": "Critical",
  "confidence": "High"
}
\`\`\`

---

## 🤖 How It Works

The agent uses an **agentic loop** — autonomous decision-making between two research tools and structured output generation:

\`\`\`
1. User submits a threat topic via REST API
        ↓
2. Claude (Anthropic API) decides which tool to use first
        ↓
3. RAG retrieval over internal CISA/FBI/NSA/NCSC advisories (ChromaDB)
        ↓
4. Web search via DuckDuckGo for current intelligence
        ↓
5. Claude evaluates findings - searches more if needed
        ↓
6. Synthesizes structured JSON threat brief
        ↓
7. API returns analyst-ready brief
\`\`\`

The key insight: **Claude autonomously decides when to search, which tool to use, what to query, and when it has enough information** — that's what makes this system agentic.

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM | Anthropic Claude API |
| Agent Framework | LangChain |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Web Search | DuckDuckGo |
| API Framework | FastAPI |
| Server | Uvicorn |
| PDF Processing | PyPDF |

---

## 📁 Project Structure

\`\`\`
cyber-threat-agent/
├── agent/
│   ├── __init__.py
│   ├── core.py           # Main agentic loop and orchestration
│   ├── tools.py          # Tool definitions (web_search + RAG)
│   └── prompts.py        # System prompt and threat brief schema
├── rag/
│   ├── __init__.py
│   ├── ingest.py         # Builds the ChromaDB knowledge base
│   └── retriever.py      # Searches the knowledge base
├── api/
│   ├── __init__.py
│   └── main.py           # FastAPI REST endpoints
├── data/
│   ├── sample_reports/   # CISA, FBI, NCSC threat intel PDFs
│   └── chroma_db/        # ChromaDB persistent vector store
├── briefs/               # Saved JSON threat brief outputs
├── main.py               # CLI entry point
├── requirements.txt      # All dependencies
├── .env                  # API keys (not committed)
├── .gitignore
└── README.md
\`\`\`

---

## ⚙️ Quickstart

### Prerequisites
- Python 3.10+
- Anthropic API key ([get one here](https://console.anthropic.com))

### 1. Clone and set up
\`\`\`bash
git clone https://github.com/Nyansaa/Cyber-Threat-Agent.git
cd Cyber-Threat-Agent

python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
\`\`\`

### 2. Configure your API key
Create a \`.env\` file in the root directory:
\`\`\`
ANTHROPIC_API_KEY=your-key-here
\`\`\`

### 3. Build the knowledge base
Add cybersecurity advisory PDFs to \`data/sample_reports/\`, then run:
\`\`\`bash
python -m rag.ingest
\`\`\`

### 4. Run the agent

**Option A — Terminal mode:**
\`\`\`bash
python main.py
\`\`\`

**Option B — REST API mode:**
\`\`\`bash
python -m api.main
\`\`\`

Then open \`http://localhost:8000/docs\` for interactive API documentation.

---

## 🔌 API Usage

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Service info and endpoint list |
| GET | /health | Health check |
| GET | /docs | Interactive Swagger UI documentation |
| POST | /research | Submit a threat topic for analysis |

### Example: Python
\`\`\`python
import requests

response = requests.post(
    "http://localhost:8000/research",
    json={"threat_topic": "LockBit ransomware targeting healthcare"}
)
brief = response.json()
print(brief["summary"])
\`\`\`

### Example: curl
\`\`\`bash
curl -X POST 'http://localhost:8000/research' \
  -H 'Content-Type: application/json' \
  -d '{"threat_topic": "APT29 phishing campaign"}'
\`\`\`

---

## 🎯 Relevance to Defense & Intelligence

This project directly mirrors workflows used by CTI teams at defense contractors and government agencies:

- **Structured threat briefs** follow formats used in real SOC and intelligence environments
- **RAG over authoritative sources** (CISA, FBI, NSA, NCSC) ensures grounded, citable analysis
- **MITRE ATT&CK-aligned** terminology throughout (TTPs, IoCs, threat actors)
- **REST API architecture** enables integration with SIEM, SOAR, and intel platforms
- **Agentic design** reflects how modern AI is deployed in defense AI programs

The same architecture pattern applies to **any compliance, policy, or knowledge-base domain** where an AI agent needs to combine authoritative documents with real-time information.

---

## 🗺️ Roadmap

- [x] **Part 1** — Core agentic loop with Claude API and web search
- [x] **Part 2** — Structured JSON threat brief output
- [x] **Part 3** — RAG integration with ChromaDB
- [x] **Part 4** — FastAPI REST endpoint with auto-generated docs
- [x] **Part 5** — Production-ready documentation and quickstart

### Future enhancements
- [ ] Streamlit frontend for non-technical analyst access
- [ ] Docker containerization for deployment
- [ ] MITRE ATT&CK technique extraction and linking
- [ ] STIX/TAXII output format support
- [ ] Authentication and rate limiting for production deployment

---

## 👩🏾‍💻 Author

**Anita Adu Amofah**  
Computer Science & Cybersecurity (Double Major) | Fayetteville State University | May 2027  
AI Research | NASA Collaboration | Defense & Intelligence Focus

[GitHub](https://github.com/Nyansaa)

---

## ⚠️ Disclaimer

This tool is built for educational and portfolio purposes. All threat intelligence retrieved comes from publicly available government sources. Not intended for offensive security purposes.
