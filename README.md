# Q&A bot with RAG implementation

A **Retrieval-Augmented Generation (RAG) Chat Application** that allows users to upload documents with various file extensions and query them via a chatbot interface and get answers and citations. Built with **FastAPI** backend and **React + Material UI** frontend and used **Google Embeddings** to generate embeddings and used **ChromaDB** as default vector storage.

---

## Features

- Upload various types of documents such as pdf, csv, text, html, json. (support for many more file types in future...)
- Ask questions about uploaded documents.
- Chat interface with user and bot messages.
- Receive llm response with citations
   - about the source file
   - source file paragraph

---

## System Architecture
![RAG application system architecture](https://github.com/jeeva1429/gen-ai-bot/blob/main/rag-bot-design.png)

## Tech Stack

**Backend:**
- Python 3.13+
- FastAPI standard
- LangChain
- Google Generative AI Embeddings (or OpenAI embeddings)
- Chroma for vector storage

**Frontend:**
- React 18
- TypeScript
- Material UI (MUI)
- Vite for fast development

