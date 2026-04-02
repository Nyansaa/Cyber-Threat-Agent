# 🛡️ Cyber Threat Intelligence (CTI) Agent

An agentic AI system that autonomously researches cyber threats and produces structured, 
analyst-ready threat briefs for defense and intelligence applications.

Built to mirror real-world CTI workflows used by defense contractors and government agencies.

---

## 📌 Overview

The CTI Agent accepts a cyber threat topic, autonomously searches the web for current 
threat intelligence, and returns a structured threat brief — including threat actors, 
targeted sectors, attack vectors, indicators of compromise (IoCs), and recommended mitigations.

This project demonstrates applied agentic AI in a defense and intelligence context, 
combining large language model reasoning with real-time web retrieval to automate 
analyst workflows.

---

## 🎯 Use Case

Defense contractors, government agencies, and intelligence community analysts spend 
significant time manually researching threats and writing briefs. This agent automates 
that research pipeline — giving analysts a structured starting point in seconds instead of hours.

**Example prompt:** `APT29 phishing campaign targeting government networks`

**Example output:**
```json
{
  "threat_name": "APT29 (Cozy Bear) Spearphishing Campaign",
  "threat_type": "Advanced Persistent Threat (APT) / Spearphishing",
  "summary": "APT29, a Russian SVR-affiliated threat actor, has conducted sustained 
               spearphishing campaigns targeting government networks, think tanks, and 
               defense contractors using malicious OAuth applications and credential 
               harvesting techniques.",
  "threat_actors": ["APT29", "Cozy Bear", "Midnight Blizzard"],
  "targeted_sectors": ["Government", "Defense", "Think Tanks", "NGOs"],
  "attack_vectors": [
    "Spearphishing emails with malicious links",
    "OAuth application abuse for persistent access",
    "Password spray attacks against cloud services"
  ],
  "indicators_of_compromise": [
    "Suspicious OAuth app consent requests",
    "Unusual authentication from foreign IPs",
    "Unexpected MFA prompts"
  ],
  "mitigations": [
    "Enable phishing-resistant MFA across all accounts",
    "Audit and restrict OAuth application permissions",
    "Monitor for anomalous login activity and credential stuffing"
  ],
  "severity": "Critical",
  "confidence": "High"
}
```

---

## 🤖 How It Works

This agent uses an **agentic loop** — a back-and-forth between the AI and external tools 
until the task is complete. Here's what happens when you enter a threat topic:

```
1. You enter a threat topic
        ↓
2. Claude (via Anthropic API) reads the system prompt and decides to search
        ↓
3. Agent calls DuckDuckGo web search tool with a targeted query
        ↓
4. Search results are returned to Claude
        ↓
5. Claude decides if it needs more information → searches again if needed
        ↓
6. Claude synthesizes findings into a structured JSON threat brief
        ↓
7. Brief is displayed in the terminal and saved to briefs/ folder
```

The key insight: **Claude autonomously decides when to search, what to search for, 
and when it has enough information** — that's what makes this system "agentic."

---

## 🧰 Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core programming language |
| Anthropic Claude API | LLM brain of the agent (`claude-sonnet-4-6`) |
| LangChain | Agent framework and tool integration |
| DuckDuckGo Search | Real-time web retrieval (no API key required) |
| python-dotenv | Secure API key management |
| ChromaDB *(coming)* | Vector database for RAG integration |
| FastAPI *(coming)* | REST API interface for deployment |

---

## 📁 Project Structure

```
cyber-threat-agent/
├── agent/
│   ├── __init__.py       # Package entry point
│   ├── core.py           # Main agentic loop and orchestration
│   ├── tools.py          # Web search tool definition and router
│   └── prompts.py        # System prompt and threat brief schema
├── rag/                  # RAG integration (Part 3 — in progress)
├── api/                  # FastAPI interface (Part 4 — coming soon)
├── data/
│   └── sample_reports/   # Threat intelligence PDFs for RAG
├── briefs/               # Saved JSON threat brief outputs
├── .env                  # API keys (not committed)
├── .gitignore
├── main.py               # Entry point — run this to start the agent
├── requirements.txt      # All dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Anthropic API key ([get one here](https://console.anthropic.com))

### 1. Clone the repository
```bash
git clone git clone https://github.com/Nyansaa/cyber-threat-agent.git
cd cyber-threat-agent
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the root directory:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 5. Run the agent
```bash
python main.py
```

### 6. Enter a threat topic when prompted
```
Enter threat topic (or 'quit' to exit):
> LockBit ransomware targeting critical infrastructure
```

---

## 📋 Requirements

Create a `requirements.txt` by running:
```bash
pip freeze > requirements.txt
```

Or install manually:
```
anthropic
langchain
langchain-community
duckduckgo-search
ddgs
python-dotenv
```

---

## 🗺️ Roadmap

- [x] **Part 1** — Core agentic loop with Claude API and web search
- [x] **Part 2** — Structured JSON threat brief output
- [ ] **Part 3** — RAG integration with ChromaDB for threat intel document retrieval
- [ ] **Part 4** — FastAPI REST endpoint and Streamlit frontend
- [ ] **Part 5** — Deployment, demo GIF, and full documentation

---

## 🎯 Relevance to Defense & Intelligence

This project directly mirrors workflows used by CTI teams at defense contractors 
and government agencies:

- **Structured threat briefs** follow formats used in real SOC and intel environments
- **MITRE ATT&CK aligned** terminology (TTPs, IoCs, threat actors)
- **Agentic architecture** reflects how modern AI is being deployed in defense AI programs
- **Designed for extensibility** — RAG layer will enable ingestion of classified-format reports

---

## 👩🏾‍💻 Author

**Anita Amofah**  
Computer Science & Cybersecurity (Double Major) | Fayetteville State University | May 2027  
AI Research | NASA Collaboration | Defense & Intelligence Focus

[LinkedIn](https://www.linkedin.com/in/anita-amofah/) • [Portfolio](https://anita-amofah.netlify.app/) • [GitHub](https://github.com/Nyansaa)

---

## ⚠️ Disclaimer

This tool is built for educational and portfolio purposes. All threat intelligence 
retrieved is from publicly available sources. Do not use for offensive security purposes.
