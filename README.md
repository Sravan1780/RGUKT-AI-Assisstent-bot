# 🎓 RGUKT AI Assistant Bot

A RAG-based (Retrieval-Augmented Generation) AI chatbot that answers institutional academic queries for RGUKT (Rajiv Gandhi University of Knowledge Technologies). Built with LangChain, ChromaDB, LLaMA 3 via Groq, React, and FastAPI.

---

## 🚀 Features

- 📄 Ingests 1000+ pages of PDF data (Academic Regulations, About RGUKT) using PyPDF
- 🌐 Scrapes live content from RGUKT official website using BeautifulSoup
- 🔍 Semantic search using ChromaDB vector database with LangChain embeddings
- 🤖 LLaMA 3 (via ChatGroq) for accurate, context-aware responses
- ⚡ Sub-second retrieval of relevant chunks using RAG pipeline
- 💬 Clean React + Vite frontend with Tailwind CSS
- 🔗 FastAPI backend with RESTful API

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Axios |
| Backend | FastAPI, Uvicorn, Python |
| LLM | LLaMA 3.3 via ChatGroq |
| RAG | LangChain, ChromaDB |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| PDF Parsing | PyPDF |
| Web Scraping | BeautifulSoup4, Requests |

---

## 📁 Project Structure

```
rgukt-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py          # FastAPI app, RAG chain, chat endpoint
│   ├── rgukt_datasets/      # PDF source files
│   │   ├── about_rgukt.pdf
│   │   └── Academic_Regulations_Hand_Book.pdf
│   ├── rgukt2_db/           # ChromaDB vector store (auto-generated)
│   ├── requirements.txt
│   ├── run.py               # Uvicorn server entry point
│   └── .env                 # Your API keys (not committed)
├── frontend/
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/)

---

### 1. Clone the repository

```bash
git clone https://github.com/Sravan1780/RGUKT-AI-Assisstent-bot.git
cd RGUKT-AI-Assisstent-bot
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside the `backend/` folder:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

### 3. Build the Vector Database

Run this once to index the PDFs into ChromaDB:

```bash
python rebuild_db.py
```

You should see:
```
✅ Vector database built successfully at .../backend/rgukt2_db
```

---

### 4. Start the Backend

```bash
python run.py
```

API will be available at: `http://localhost:8000`

---

### 5. Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Component status |
| POST | `/api/chat` | Send a chat message |
| POST | `/api/clear-history` | Clear chat history |

### Example Request

```json
POST /api/chat
{
  "text": "What are the attendance requirements at RGUKT?",
  "chat_history": []
}
```

---

## 💡 Example Questions to Ask

- What is the minimum GPA required to pass at RGUKT?
- What happens if a student fails in RGUKT exams?
- How does the admission process work at RGUKT?
- What are the hostel facilities at RGUKT?
- Tell me about RGUKT's CSE department.

---

## 🧠 How It Works

```
User Query
    │
    ▼
HuggingFace Embeddings (all-MiniLM-L6-v2)
    │
    ▼
ChromaDB Semantic Search → Top 5 relevant chunks
    │
    ▼
LangChain RAG Chain + LLaMA 3 (ChatGroq)
    │
    ▼
Structured HTML Response → React Frontend
```

If the RAG chain doesn't find a confident answer, the bot falls back to scraping live content from the RGUKT website using section-specific agents.

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `no such column: collections.topic` | Delete `rgukt2_db/` folder and run `rebuild_db.py` |
| `model decommissioned` | Change model name in `main.py` to `llama-3.3-70b-versatile` |
| `Vector database not found` | Run `rebuild_db.py` to build the ChromaDB index |
| `GROQ_API_KEY not set` | Add your key to `backend/.env` |

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

**Sravan Kumar Panchakoti**  
[GitHub](https://github.com/Sravan1780)