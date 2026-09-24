"""
Free RAG pipeline: Ollama (local LLM) + Chroma (local vector DB).
No API keys. No cloud. 100% private. Runs entirely on your machine.

Prerequisites:
  - Ollama running: ollama serve
  - Model pulled: ollama pull llama3.2
  - pip install -r requirements.txt
"""

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from ollama import Client

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2"
COLLECTION_NAME = "my_docs"

ollama = Client(host=OLLAMA_HOST)
chroma = chromadb.Client()
embed_fn = OllamaEmbeddingFunction(url=f"{OLLAMA_HOST}/api/embeddings", model_name=MODEL)
collection = chroma.get_or_create_collection(COLLECTION_NAME, embedding_function=embed_fn)


def add_documents(docs: list[str], ids: list[str] | None = None) -> None:
    if ids is None:
        ids = [str(i) for i in range(len(docs))]
    collection.add(documents=docs, ids=ids)
    print(f"✅ Added {len(docs)} document(s) to the knowledge base.")


def query(question: str, n_results: int = 3) -> str:
    results = collection.query(query_texts=[question], n_results=n_results)
    context = "\n\n".join(results["documents"][0])

    prompt = f"""Answer the question using only the context below.
If the answer isn't in the context, say "I don't know."

Context:
{context}

Question: {question}
Answer:"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


if __name__ == "__main__":
    # Example: load some documents
    sample_docs = [
        "Groq offers a free tier with 14,400 requests per day for Llama 3.3 70B.",
        "Ollama lets you run LLMs locally with a single command: ollama run llama3.2.",
        "Chroma is an open-source vector database that runs entirely in-memory or on disk.",
        "The free AI Bible is a curated list of free AI tools and APIs for developers.",
    ]
    add_documents(sample_docs)

    print("\n🔍 RAG Pipeline Ready — ask anything about your documents.")
    print("   Type 'exit' to quit\n")

    while True:
        q = input("Question: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue
        answer = query(q)
        print(f"\nAnswer: {answer}\n")
