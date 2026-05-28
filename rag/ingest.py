# rag/ingest.py
# -------------
# This file loads PDFs, chunks them, and stores in ChromaDB.
# Run this once to build your knowledge base.

import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# ─── CONFIGURATION ────────────────────────────────────────────────────────────

# Where your PDF reports live
REPORTS_DIR = "data/sample_reports"

# Where ChromaDB will store the vector database on disk
CHROMA_DIR = "data/chroma_db"

# The embedding model — runs locally, no API key needed
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunk settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
# ─── LOAD PDFS ────────────────────────────────────────────────────────────────

def load_pdfs(reports_dir: str) -> list:
    """
    Find and load all PDF files from the reports directory.
    Returns a list of Document objects — one per page.
    """
    documents = []
    reports_path = Path(reports_dir)
    
    # Find all PDF files in the folder
    pdf_files = list(reports_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"  [⚠ Warning]: No PDF files found in {reports_dir}")
        return []
    
    print(f"\n  [📄 Loading]: Found {len(pdf_files)} PDF file(s)")
    
    for pdf_path in pdf_files:
        print(f"  [📄 Loading]: {pdf_path.name}")
        try:
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            for page in pages:
                page.metadata["source_file"] = pdf_path.name
            documents.extend(pages)
            print(f"  [✓ Loaded]: {len(pages)} pages from {pdf_path.name}")
        except Exception as e:
            print(f"  [✗ Error]: Could not load {pdf_path.name}: {str(e)}")
    
    return documents
# ─── SPLIT INTO CHUNKS ────────────────────────────────────────────────────────

def split_documents(documents: list) -> list:
    """
    Split large documents into smaller chunks for embedding.
    """
    print(f"\n  [✂ Splitting]: {len(documents)} pages into chunks...")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"  [✓ Split]: Created {len(chunks)} chunks")
    
    return chunks
# ─── EMBED AND STORE IN CHROMADB ──────────────────────────────────────────────

def store_in_chromadb(chunks: list) -> Chroma:
    """
    Convert chunks to embeddings and store them in ChromaDB.
    """
    print(f"\n  [🧠 Embedding]: Loading embedding model ({EMBEDDING_MODEL})...")
    print(f"  [Note]: First run downloads the model (~90MB). This takes a minute.")
    
    # Initialize the embedding model
    # Runs locally — no API key needed
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )
    
    print(f"  [💾 Storing]: Writing {len(chunks)} chunks to ChromaDB...")
    
    # Create ChromaDB vector store and save to disk
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    
    print(f"  [✓ Stored]: Vector database saved to {CHROMA_DIR}")
    
    return vectorstore
# ─── MAIN INGESTION PIPELINE ──────────────────────────────────────────────────

def ingest():
    """
    Run the full ingestion pipeline:
    Load PDFs → Split into chunks → Embed → Store in ChromaDB
    """
    print("\n" + "=" * 65)
    print("       CTI KNOWLEDGE BASE INGESTION")
    print("=" * 65)
    
    # Step 1: Load all PDFs
    documents = load_pdfs(REPORTS_DIR)
    if not documents:
        print("\n[Error]: No documents to ingest. Add PDFs to data/sample_reports/")
        return None
    
    print(f"\n  [Total]: {len(documents)} pages loaded across all documents")
    
    # Step 2: Split into chunks
    chunks = split_documents(documents)
    
    # Step 3: Embed and store in ChromaDB
    vectorstore = store_in_chromadb(chunks)
    
    print("\n" + "=" * 65)
    print("  ✅ Ingestion complete! Knowledge base is ready.")
    print(f"  📚 {len(chunks)} chunks stored in ChromaDB")
    print("  🔍 The agent can now search your threat intel documents.")
    print("=" * 65 + "\n")
    
    return vectorstore


# ─── RUN DIRECTLY ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ingest()