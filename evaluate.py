import json, os, requests, numpy as np
from pypdf import PdfReader
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

print("Setting up evaluation pipeline...")
reader = PdfReader("test.pdf")
text = "".join([page.extract_text() + "\n" for page in reader.pages if page.extract_text()])
size, overlap, chunks = 500, 50, []
start = 0
while start < len(text):
    chunks.append(text[start:start+size])
    start += (size - overlap)

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    data = {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": text}]}}
    res = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
    return res.json()['embedding']['values'] if res.status_code == 200 else None

print("Embedding evaluation document...")
chunk_data = [{"chunk": c, "vector": get_embedding(c)} for c in chunks if get_embedding(c)]

with open('eval_questions.json', 'r') as f:
    eval_data = json.load(f)

passed = 0
print("\n--- Starting Evaluation ---")
for item in eval_data:
    q = item['question']
    expected = item['expected_keyword'].lower()
    
    q_vec = get_embedding(q)
    if not q_vec:
        continue
        
    scored = []
    for d in chunk_data:
        sim = np.dot(q_vec, d['vector']) / (np.linalg.norm(q_vec) * np.linalg.norm(d['vector']))
        scored.append((sim, d['chunk']))
    scored.sort(reverse=True, key=lambda x: x[0])
    top_chunks = scored[:3]
    
    context = "\n\n".join([c[1] for c in top_chunks])
    prompt = f"Answer ONLY from context. If not found, explicitly say 'I cannot answer this based on the loaded documents.'\n\nContext:\n{context}\n\nQuestion: {q}"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    res = requests.post(url, headers={'Content-Type': 'application/json'}, json={"contents": [{"parts": [{"text": prompt}]}]})
    
    try:
        answer = res.json()['candidates'][0]['content']['parts'][0]['text'].strip().lower()
        if expected in answer:
            print(f"✅ PASS: {q}")
            passed += 1
        else:
            print(f"❌ FAIL: {q}\n   Expected: {expected}\n   Got: {answer[:50]}...")
    except Exception as e:
        print(f"❌ FAIL: {q} (API Error)")
    
    time.sleep(1)

print(f"\nEvaluation Summary: {passed}/{len(eval_data)} passed.")
