# rag/retriever.py
# ----------------
# This file searches the ChromaDB knowledge base we built in ingest.py.
# When the agent needs threat intel, it calls this to find relevant chunks.

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
# These MUST match the values in ingest.py — same model, same location

CHROMA_DIR = "data/chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# ─── LOAD THE VECTOR STORE ────────────────────────────────────────────────────

def load_vectorstore() -> Chroma:
    """
    Load the existing ChromaDB knowledge base from disk.
    
    Unlike ingest.py which CREATES the database, this just OPENS
    the one we already built so we can search it.
    """
    # Load the same embedding model used during ingestion
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )
    
    # Open the existing ChromaDB from disk
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    
    return vectorstore
# ─── SEARCH FUNCTION ──────────────────────────────────────────────────────────

# Load the vectorstore once when this file is imported (reused for all searches)
_vectorstore = None

def search_documents(query: str, num_results: int = 3) -> str:
    """
    Search the knowledge base for chunks relevant to the query.
    
    Args:
        query: What to search for (e.g. "Iranian APT tactics")
        num_results: How many relevant chunks to return
        
    Returns:
        A formatted string of the most relevant chunks, with sources
    """
    global _vectorstore
    
    # Load the vectorstore the first time, then reuse it
    if _vectorstore is None:
        print("  [📚 RAG]: Loading knowledge base...")
        _vectorstore = load_vectorstore()
    
    print(f"  [📚 RAG searching]: {query}")
    
    # Search ChromaDB for the most similar chunks
    results = _vectorstore.similarity_search(query, k=num_results)
    
    if not results:
        return "No relevant documents found in the knowledge base."
    
    # Format the results into a readable string for the agent
    formatted = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source_file", "unknown")
        page = doc.metadata.get("page", "?")
        content = doc.page_content.strip()
        formatted.append(
            f"[Document {i} — Source: {source}, Page: {page}]\n{content}"
        )
    
    print(f"  [✓ RAG]: Found {len(results)} relevant chunks")
    
    return "\n\n".join(formatted)
# ─── TEST DIRECTLY ────────────────────────────────────────────────────────────
# Lets you run: python -m rag.retriever
# to test the retriever without running the full agent

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("       RAG RETRIEVER — TEST MODE")
    print("=" * 65 + "\n")
    
    # Try a sample query
    test_query = "Iranian APT actors targeting critical infrastructure"
    
    print(f"Test query: {test_query}\n")
    
    results = search_documents(test_query, num_results=3)
    
    print("\n" + "=" * 65)
    print("  RESULTS")
    print("=" * 65 + "\n")
    print(results)
    print("\n" + "=" * 65 + "\n")