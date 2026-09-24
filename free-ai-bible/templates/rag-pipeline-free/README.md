# Free RAG Pipeline — Ollama + Chroma

100% local. 100% private. No API keys. No cloud. No cost.

## Prerequisites

```bash
# 1. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2
```

## Setup

```bash
pip install -r requirements.txt
python app.py
```

## What You Get

- Full RAG pipeline in ~70 lines of Python
- Local embeddings via Ollama (no OpenAI key needed)
- In-memory vector search via Chroma
- Swap `sample_docs` for your own content (PDFs, docs, notes)
- Zero ongoing cost, runs fully offline
