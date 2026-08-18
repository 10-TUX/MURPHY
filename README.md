# 🧠 MURPHY — AI Codebase Assistant

> An intelligent AI-powered assistant that helps developers understand, navigate, and analyze software projects using Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

---

## 🚀 What is MURPHY?

MURPHY is being built as an AI-powered codebase assistant that will allow developer to **upload an entire software project** and interact with it using **natural language**.  
Instead of manually searching through hundreds of files, ask questions about the codebase and receive accurate, context-aware answers backed by the actual source code.

**Key capabilities:**

- 🔍 **Semantic Code Search** — find code by intent, not keywords
- 📖 **Code Explanation** — understand functions, classes, APIs, and design patterns
- 🏗️ **Architecture Exploration** — module relationships, data flow, dependency structure
- 🐛 **Bug Investigation** — identify logic issues, missing validations, duplicates
- 📝 **Documentation Generation** — auto-generate README sections, API summaries
- 🌐 **Multi-language Support** — Python, Java, C++, JavaScript, TypeScript, Verilog, and more

---

## 🏛️ PLANNED/TARGET Architecture

```
Repository Upload
        │
        ▼
Repository Scanner → File Filtering → Code Parsing
        │
        ▼
   Chunking → Embedding Generation → FAISS Vector Store
        │
        ▼
   Retriever → LangChain → Gemini API → AI Response
        │
        ▼
     Frontend (Streamlit)
```

---

## 🛠️ Tech Stack

| Layer          | Technology                                    |
| -------------- | --------------------------------------------- |
| **Language**   | Python                                        |
| **Backend**    | FastAPI + Uvicorn                              |
| **Frontend**   | Streamlit                                      |
| **LLM**        | Google Gemini API                              |
| **AI Framework** | LangChain                                    |
| **Embeddings** | Google Gemini Embeddings / Sentence Transformers |
| **Vector DB**  | FAISS - vector similarity  search              |
| **Parsing**    | Python AST (Tree-sitter planned)               |

---

## 📁 Project Structure

```
MURPHY/
├── main.py                  # FastAPI entry point
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
├── .env.example             # Environment template
│
├── app/
│   ├── __init__.py          # Package metadata & version
│   ├── api/                 # FastAPI route handlers
│   ├── core/                # Config, settings, constants
│   │   └── config.py        # Pydantic Settings + dotenv loader
│   ├── models/              # Pydantic schemas & data models
│   ├── services/            # Business logic (parsing, RAG, etc.)
│   └── utils/               # Helper functions
│
├── frontend/                # Streamlit application
├── tests/                   # Test suite
├── docs/                    # Documentation files
├── prompts/                 # Prompt templates for LLM
└── scripts/                 # Utility scripts
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/murphy.git
cd murphy
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 5. Run the API server

```bash
uvicorn main:app --reload --port 8000
```

Visit the interactive docs at **http://localhost:8000/docs**

---

## 📝 License

This project is for educational and portfolio purposes.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

*Built with ❤️ using Python, FastAPI, LangChain, and Google Gemini.*
