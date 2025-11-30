# 🧠 BOT-GPT — Conversational AI + RAG Prototype

### note (important)
- rename the .env_sample to .env and add gemini and openai key to test that on local system
- add the gemnini(to test the conversational ai) and opeai(for testing word embeddings RAG) key for testing 

A lightweight prototype of a **conversational AI assistant** built using:

- **Flask** (backend + routes + UI)
- **LangChain** (LLM orchestration)
- **Google Gemini (via LangChain)** for chat responses
- **OpenAI Embeddings** (`text-embedding-3-small`)
- **Pinecone** as the **vector database**
- **MySQL** as the relational database (session + messages storage)
- **Docker** for packaging and test deployment

This project is built for **experimentation and early-stage client demos** — clean, simple, and easy to understand.

---

## 🚀 Features

### ✅ Conversational AI (multi-turn chat)
- Uses LangChain’s `RunnableWithMessageHistory`
- Memory is loaded from MySQL on every request
- Cutting/deleting messages removes them from memory as well

### ✅ Session-based chat
Each conversation has its own **`session_id`**, stored in MySQL.

You can:
- list all sessions  
- view chat history  
- create new sessions  
- delete sessions  
- delete messages from any point (rewind the conversation)

### ✅ PDF Upload → Vector Store
- upload PDF files
- extract raw text
- split into text chunks
- embed using **OpenAI text-embedding-3-small**
- store embeddings in **Pinecone** under a *single namespace*
- each vector is tagged with `session_id`, `doc_id`, and `chunk_index`

### ✅ Vector Store (Pinecone)
- single namespace (e.g., `bot-gpt`)
- metadata filtering for per-session retrieval  
- ready for RAG pipeline integration

### ✅ Clean & Minimal UI
- list sessions  
- view messages  
- send messages to LLM  
- delete/cut messages  
- upload files  

### ✅ Dockerized (simple)
- `.env` is included inside the image or zip for quick testing
- run anywhere with a single command

---

## 🧱 Tech Stack

### **Backend**
- Flask

### **LLM Orchestration**
- LangChain v1+
- Google Gemini via `langchain-google-genai`
- RunnableWithMessageHistory

### **Databases**
#### 🟦 MySQL (relational)
Used for:
- `sessions`
- `messages`

#### 🟪 Pinecone (vector DB)
Used for:
- document chunks
- semantic search (RAG-ready)

Metadata format:
```json
{
  "session_id": "sess_123",
  "doc_id": "invoice.pdf",
  "chunk_index": 0
}
````

### **Embeddings**

* OpenAI `text-embedding-3-small`
  (1536 dimensions)

### **Containerization**

* Docker (Python 3.11 slim)

---

## ⚙️ How It Works

### 1️⃣ Session Layer (MySQL)

* Each chat session gets a `session_id`
* Messages stored under this session
* Deleting messages rewinds memory

### 2️⃣ Chat Flow

1. User sends a message
2. Stored in MySQL
3. LangChain loads full history from DB
4. Memory injected into LLM
5. LLM responds
6. Response stored in MySQL
7. Page reloads with updated chat

### 3️⃣ PDF → Vector Store

Flow:

1. Upload PDF
2. Extract raw text
3. Chunk into ~1000-char segments
4. Embed each chunk with OpenAI
5. Upsert into Pinecone:

   * single namespace
   * metadata carries session_id/doc_id

### 4️⃣ Retrieval (coming soon)

Later:

```python
index.query(
    vector=embed(question),
    top_k=5,
    filter={"session_id": current_session}
)
```

---

## 🏗 Project Structure

```
.
├── app.py
├── .env
├── requirements.txt
├── Dockerfile
└── app/
    ├── __init__.py
    ├── config.py
    ├── chat_flow.py
    ├── database/
    │   ├── relational.py
    │   └── vector_store.py
    ├── utils/
    ├── templates/
    └── static/
```

---

## ▶️ Running the App

### Without Docker

```bash
pip install -r requirements.txt
python app.py
```

Visit:

```
http://localhost:5000/sessions
```

---

### With Docker

```bash
docker build -t bot-gpt .
docker run -p 5000:5000 bot-gpt
```

No env flags needed — `.env` is inside the image.

---

## 📌 Notes

* This is a prototype → intentionally simple
* No user accounts
* No advanced preprocessing
* No production security
* Only features needed for demo/testing included

---

## 📚 Upcoming Enhancements

* Retrieval chain (RAG)
* PDF viewer in UI
* Markdown / JSON export of chats
* Auto-summarization for long memory
* Model selector
* Multi-file upload
* Async background embedding

---

## 🎉 Summary

**BOT-GPT** is a simple, clean prototype demonstrating:

* multi-turn conversational AI
* persistent memory
* document ingestion
* vector storage
* early RAG pipeline
* working UI & backend demo