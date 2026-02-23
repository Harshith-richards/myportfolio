# NEXUS — Neural EXecution and Understanding System

NEXUS is a modular, production-oriented multi-agent autonomous AI framework designed for solo developers and small teams.

## Architecture

```
UI (CLI / Streamlit / API)
  -> OrchestratorAgent
     -> PlanningEngine + Memory System
     -> AgentRegistry (Research, Code, File, Data, API, QA, Reflection, Memory)
     -> ToolRegistry (web, code, files, SQL, API, email, scheduler)
```

## Quickstart

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   ```
3. Run API:
   ```bash
   uvicorn nexus.api.main:app --reload
   ```
4. Run dashboard:
   ```bash
   streamlit run nexus/dashboard/app.py
   ```

## Demo scenarios

Run all required demo goals:

```bash
python scripts/demo.py
```

## Safety model

- Permission levels (`READ_ONLY`, `STANDARD`, `ELEVATED`, `ADMIN`).
- Optional human-in-loop approval gate.
- Tool-level rate limits.
- Sandboxed code execution policy settings.

## FAQ

- **Can I swap LLM providers?** Yes, use OpenAI, Anthropic, Ollama, or fallback chaining.
- **Can I add custom agents/tools?** Yes, drop plugin classes in `nexus/plugins`.
- **How is memory handled?** Short-term in-memory + persistent ChromaDB + episodic traces.
