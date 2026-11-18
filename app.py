import os, requests, json
import numpy as np
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

def extract_text(pdf_path):
    print(f"\nExtracting text from {pdf_path}...")
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def chunk_text(text, size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (size - overlap)
    return chunks

def get_embedding(text, api_key):
    # Perfect embedding model URL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['embedding']['values']
        else:
            print(f"\nEmbedding API Error: {response.text}")
            return None
    except Exception as e:
        return None

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed_and_cache(chunks, pdf_path, api_key):
    cache_file = f"{pdf_path}.json"
    if os.path.exists(cache_file):
        print("Loading embeddings from cache...")
        with open(cache_file, 'r') as f:
            return json.load(f)
            
    print("Generating embeddings...")
    chunk_data = []
    for chunk in chunks:
        vector = get_embedding(chunk, api_key)
        if vector:
            chunk_data.append({"chunk": chunk, "vector": vector, "source": pdf_path})
            
    with open(cache_file, 'w') as f:
        json.dump(chunk_data, f)
    return chunk_data

def retrieve(question, chunk_data, api_key, top_k=3):
    q_vector = get_embedding(question, api_key)
    if not q_vector:
        return []
        
    scored_chunks = []
    for data in chunk_data:
        sim = cosine_similarity(q_vector, data['vector'])
        scored_chunks.append((sim, data['chunk'], data['source']))
        
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return scored_chunks[:top_k]

def answer_question(question, retrieved_chunks, api_key):
    if not retrieved_chunks:
        return "No relevant context found."
        
    context = "\n\n".join([f"Source: {c[2]}\nText: {c[1]}" for c in retrieved_chunks])
    prompt = f"Answer the question based ONLY on the provided context.\n\nContext:\n{context}\n\nQuestion: {question}"
    
    # Perfect generation model URL (Removed '-latest')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"Answer API Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Error: {e}"

print("Welcome to DocuMind Week 3 (RAG System)!")
file_path = input("Enter PDF file path: ")
raw_text = extract_text(file_path)

if raw_text:
    chunks = chunk_text(raw_text)
    chunk_data = embed_and_cache(chunks, file_path, api_key)
    
    while True:
        question = input("\nAsk a question (or 'quit'): ")
        if question.lower() == 'quit':
            break
            
        print("Searching...")
        best_chunks = retrieve(question, chunk_data, api_key)
        answer = answer_question(question, best_chunks, api_key)
        
        print("\nAnswer:\n", answer)
