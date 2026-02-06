# House MD Chatbot Backend

This is the backend to the [House MD Chatbot Frontend](https://github.com/jmigsan/housemdchatbot-frontend) and is designed to work with that repo.

**A sarcastic, diagnostic AI chatbot emulating Dr. Gregory House from _House M.D._**
This project uses **FastAPI**, **WebSockets**, **Gemini**, and **Pinecone** to deliver real-time, medically informed (and snarky) responses.

---

## 🌟 Features

- **Real-time WebSocket communication** for instant responses.
- **Semantic search** with Pinecone and Sentence Transformers to fetch relevant medical knowledge.
- **Dr. House’s personality**: Sarcastic, blunt, and diagnostically brilliant.
- **Dynamic RAG (Retrieval-Augmented Generation)** for context-aware answers.

---

## 🛠 Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python)
![Pinecone](https://img.shields.io/badge/Pinecone-4B275F?style=for-the-badge&logo=pinecone)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google)
![WebSockets](https://img.shields.io/badge/WebSockets-000000?style=for-the-badge&logo=websocket)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11
- API keys for **Pinecone**, **Gemini**, and **RunPod** (see `.env.example`).

### Installation

1. Clone the repo:
    ```bash
    git clone https://github.com/jmigsan/housemdchatbot-backend.git
    cd housemdchatbot-backend
    ```

### Running

```
uv run uvicorn app.main:app --reload
```
