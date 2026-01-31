# [Nákupák](https://nakupak.slama.dev/)

A vibecoded web app for managing my family shopping list, since I wanted something that I can
- edit from the **web** from any device,
- support **real-time updates** when multiple people add items to the list, and
- work **offline** when shopping since the store I go to doesn't have internet coverage

It's pure vibe, so proceed with caution.

## Development

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### LLM Worker

Recipe import uses an LLM (via Ollama) to extract structured data from recipe pages.
The inference runs on a separate machine that connects to the server over WebSocket.

```bash
cd worker
uv run llm_worker.py
```
