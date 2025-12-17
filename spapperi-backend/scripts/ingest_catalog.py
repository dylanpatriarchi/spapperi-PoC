
import asyncio
import os
import sys
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
import asyncpg
from pgvector.asyncpg import register_vector

# Configuration
PDF_PATH = "/app/source/catalogo.pdf"
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DATABASE_URL:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY not set")
    sys.exit(1)

async def main():
    print(f"Starting ingestion for {PDF_PATH}...")
    
    if not os.path.exists(PDF_PATH):
        print(f"Error: File {PDF_PATH} not found")
        sys.exit(1)

    # 1. Load PDF
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")

    # 2. Split Text
    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    docs = text_splitter.split_documents(pages)
    print(f"Created {len(docs)} chunks")

    # 3. Generate Embeddings
    print("Generating embeddings...")
    embeddings_model = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )
    
    # Batch processing for embeddings/insertion to avoid potential limits/timeouts
    batch_size = 100
    
    # 4. Connect to DB
    print("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    await register_vector(conn)

    # Clear existing products? For now, let's assume we append or clear. 
    # Let's clear to avoid duplicates if re-running.
    await conn.execute("DELETE FROM products")
    print("Cleared existing products table")

    try:
        # Prepare statement
        stmt = await conn.prepare("""
            INSERT INTO products (name, description, category, embedding, metadata)
            VALUES ($1, $2, $3, $4, $5)
        """)

        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{len(docs)//batch_size + 1}...")
            
            # Extract texts for embedding
            texts = [d.page_content for d in batch]
            
            # Generate vectors
            vectors = await embeddings_model.aembed_documents(texts)
            
            # Insert into DB
            for j, doc in enumerate(batch):
                vector = vectors[j]
                
                # Basic metadata extraction (could be refined with LLM later)
                # For now, description is the chunk text
                # Name is "Catalogo Page X"
                # Category could be inferred or hardcoded
                
                page_num = doc.metadata.get("page", 0) + 1
                source = doc.metadata.get("source", "catalogo")
                
                name = f"Catalogo Spapperi - Pagina {page_num}"
                description = doc.page_content
                category = "General" # Placeholder
                metadata = {"page": page_num, "source": source}
                
                # Prepare metadata as proper JSON string
                import json
                metadata_json = json.dumps(metadata)
                
                await conn.execute("""
                    INSERT INTO products (name, description, category, embedding, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """, name, description, category, vector, metadata_json)

        print("Ingestion complete!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
