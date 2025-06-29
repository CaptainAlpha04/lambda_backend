# rag.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2') 

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def embed_chunks(chunks):
    return model.encode(chunks, show_progress_bar=True)

def create_faiss_index(vectors):
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    return index

def retrieve_top_chunks(query, chunks, index, k=5):
    query_vec = model.encode([query])
    D, I = index.search(query_vec, k)
    return [chunks[i] for i in I[0]]
