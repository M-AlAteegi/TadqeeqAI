"""
ShariaGuide - Embedding Generator
==================================
This script converts text chunks into vector embeddings and stores them
in ChromaDB for semantic search.

WHAT ARE EMBEDDINGS?
- Each chunk of text gets converted to a list of 384 numbers
- These numbers represent the "meaning" of the text
- Similar meanings = similar numbers = close in vector space
- This enables "search by meaning" not just "search by keywords"

USAGE:
    python create_embeddings.py

INPUT:  knowledge_base_english.json
OUTPUT: ./chroma_db/ (persistent vector database)
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import time


def main():
    print("=" * 55)
    print("ShariaGuide - Embedding Generator")
    print("=" * 55)
    
    # =========================================================
    # STEP 1: Load the chunked knowledge base
    # =========================================================
    input_file = Path('knowledge_base_english.json')
    
    print(f"\n[1/4] Loading chunks from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"      Loaded {len(chunks)} chunks")
    
    # =========================================================
    # STEP 2: Initialize the embedding model
    # =========================================================
    print(f"\n[2/4] Loading embedding model...")
    print(f"      Model: all-MiniLM-L6-v2 (384 dimensions)")
    print(f"      This may take a moment on first run...")
    
    # all-MiniLM-L6-v2 is:
    # - Fast (good for prototypes)
    # - Small (80MB)
    # - Decent quality for English text
    # For production, consider: all-mpnet-base-v2 (better but slower)
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"      Model loaded!")
    
    # =========================================================
    # STEP 3: Create embeddings for all chunks
    # =========================================================
    print(f"\n[3/4] Generating embeddings...")
    
    # Extract just the text for embedding
    texts = [chunk['text'] for chunk in chunks]
    
    # Generate embeddings (this is the heavy lifting)
    start_time = time.time()
    embeddings = model.encode(texts, show_progress_bar=True)
    elapsed = time.time() - start_time
    
    print(f"      Generated {len(embeddings)} embeddings in {elapsed:.1f}s")
    print(f"      Each embedding: {len(embeddings[0])} dimensions")
    
    # =========================================================
    # STEP 4: Store in ChromaDB
    # =========================================================
    print(f"\n[4/4] Storing in ChromaDB...")
    
    # Create persistent database (survives restarts)
    db_path = "./chroma_db"
    client = chromadb.PersistentClient(path=db_path)
    
    # Delete existing collection if it exists (fresh start)
    try:
        client.delete_collection("sharia_guide")
        print(f"      Deleted existing collection")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name="sharia_guide",
        metadata={"description": "Saudi regulatory documents for Islamic finance"}
    )
    
    # Prepare data for ChromaDB
    ids = []
    metadatas = []
    documents = []
    
    for i, chunk in enumerate(chunks):
        # Unique ID for each chunk
        ids.append(f"chunk_{i}")
        
        # Metadata (source, article ID) - useful for citations later
        metadatas.append({
            "source": chunk['source'],
            "chunk_id": chunk['chunk_id']
        })
        
        # The actual text
        documents.append(chunk['text'])
    
    # Add everything to the collection
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        documents=documents
    )
    
    print(f"      Stored {collection.count()} chunks in ChromaDB")
    print(f"      Database location: {db_path}/")
    
    # =========================================================
    # DONE!
    # =========================================================
    print(f"\n" + "=" * 55)
    print("SUCCESS!")
    print("=" * 55)
    print(f"\nYour vector database is ready at: {db_path}/")
    print(f"Total chunks indexed: {collection.count()}")
    print(f"\nNext step: Build the query interface!")


if __name__ == "__main__":
    main()
