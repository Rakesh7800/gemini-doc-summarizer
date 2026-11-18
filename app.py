import streamlit as st
import os, requests, numpy as np
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

st.set_page_config(page_title="DocuMind RAG", page_icon="📄")
st.title("📄 DocuMind: Chat with your PDFs")

if "chunk_data" not in st.session_state:
    st.session_state.chunk_data = []
if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_embedding(text, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={key}"
    data = {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": text}]}}
    try:
        res = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
        if res.status_code == 200:
            return res.json()['embedding']['values']
    except: return None
    return None

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)
    if st.button("Process Documents") and uploaded_files:
        with st.spinner("Processing documents..."):
            all_text = ""
            for file in uploaded_files:
                reader = PdfReader(file)
                all_text += "".join([page.extract_text() + "\n" for page in reader.pages if page.extract_text()])
            
            size, overlap, chunks = 500, 50, []
            start = 0
            while start < len(all_text):
                chunks.append(all_text[start:start+size])
                start += (size - overlap)
            
            st.session_state.chunk_data = []
            progress_bar = st.progress(0)
            for i, c in enumerate(chunks):
                vec = get_embedding(c, api_key)
                if vec: st.session_state.chunk_data.append({"chunk": c, "vector": vec})
                progress_bar.progress((i + 1) / len(chunks))
            
            st.session_state.doc_stats = {"files": len(uploaded_files), "chunks": len(st.session_state.chunk_data)}
            st.success("Documents processed and ready!")
    
    if st.session_state.doc_stats:
        st.info(f"Loaded {st.session_state.doc_stats['files']} file(s) | {st.session_state.doc_stats['chunks']} knowledge chunks")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "source" in msg: st.caption(f"Source: {msg['source'][:100]}...")

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    if not st.session_state.chunk_data:
        response = "Please upload and process a PDF document first."
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        q_vec = get_embedding(prompt, api_key)
        if q_vec:
            scored = [(cosine_sim(q_vec, d['vector']), d['chunk']) for d in st.session_state.chunk_data]
            scored.sort(reverse=True, key=lambda x: x[0])
            context = "\n\n".join([c[1] for c in scored[:3]])
            
            rag_prompt = f"Answer ONLY from context. If not found, explicitly say 'I cannot answer this based on the loaded documents.'\n\nContext:\n{context}\n\nQuestion: {prompt}"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            with st.chat_message("assistant"):
                try:
                    res = requests.post(url, headers={'Content-Type': 'application/json'}, json={"contents": [{"parts": [{"text": rag_prompt}]}]})
                    answer = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.caption(f"Source context: {scored[0][1][:150]}...")
                    st.session_state.messages.append({"role": "assistant", "content": answer, "source": scored[0][1]})
                except Exception as e:
                    st.error("Error connecting to Gemini API.")
