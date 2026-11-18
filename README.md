# SkillMe Document Summarizer

A simple Python command-line tool that reads a `.txt` file and generates a 3-bullet-point summary using the Google Gemini API. It automatically scans the Gemini models available on your API key and uses the first one that works, avoiding quota or model deprecation errors.

## Features
* Summarizes any plain-text (`.txt`) file in 3 bullet points.
* Auto-detects available Gemini models.
* Loads the API key securely from a `.env` file.
* Interactive loop: summarize multiple files, type `quit` to exit.
* Handles missing files, empty files, and network/API errors.

## Requirements
* Python 3.8 or higher
* A Gemini API key (free from Google AI Studio)
* Python packages: `requests`, `python-dotenv`

## Project Structure
```text
skillme-summarizer/
├── app.py           # main script
├── .env             # your API key (DO NOT commit this)
├── requirements.txt # dependencies
└── README.md

### Week 2 Updates: Interactive Document Processing
Added new commands to interact with the document summary:
- **`key_points`**: Extracts 5-8 main bullet points from the document.
- **`quiz_me`**: Generates 3-5 quiz questions with answers for revision.
- **`ask`**: Allows users to ask a follow-up question based on the document context.

### Week 3 Updates: Retrieval-Augmented Generation (RAG)
- **PDF Processing**: Extracted and chunked text from PDFs using `pypdf`.
- **Embeddings**: Generated and cached vector embeddings using `gemini-embedding-001`.
- **RAG Pipeline**: Built a semantic search and Q&A system using cosine similarity and `gemini-2.5-flash` to answer questions directly from the uploaded document context.

### Week 4 Updates: Web Interface & Evaluation Pipeline
- **Streamlit Web App**: Built a fully interactive web application (`app.py`) using Streamlit, allowing users to visually upload PDFs and chat with them.
- **Automated Testing**: Created an evaluation pipeline (`evaluate.py`) to automatically test the RAG system's accuracy against predefined questions in `eval_questions.json`.
- **End-to-End Integration**: Connected PDF text extraction (`pypdf`), vector embeddings (Gemini), and semantic search into a seamless UI experience.
