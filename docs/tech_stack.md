# Technology Stack

The AI Codebase Assistant combines modern Generative AI technologies with scalable backend architecture to create an intelligent developer assistant capable of understanding and analyzing software repositories.

---

# Programming Language

## Python

Python is the primary language used throughout the project.

Responsibilities:

- Backend development
- AI pipeline
- Repository processing
- API integration
- Data handling

---

# Backend Framework

## FastAPI

FastAPI powers the REST API responsible for communication between the frontend and the AI engine.

Responsibilities:

- Repository upload
- Query handling
- Response generation
- Session management
- API endpoints

---

# Frontend

## Streamlit

Provides an interactive interface for developers.

Features:

- Repository upload
- Chat interface
- Source reference display
- Conversation history
- Search panel

(Future versions may use React for a richer UI.)

---

# Large Language Model (LLM)

## Google Gemini API

Primary language model used for reasoning over retrieved code.

Responsibilities:

- Code explanation
- Architecture understanding
- Question answering
- Documentation generation
- Suggesting improvements

---

# AI Framework

## LangChain

Coordinates the Retrieval-Augmented Generation pipeline.

Responsibilities:

- Prompt templates
- Retriever pipeline
- Conversation chains
- Context management
- LLM interaction

---

# Embedding Model

## Google Gemini Embeddings

or

## HuggingFace Sentence Transformers

Purpose:

Convert source code and natural language queries into semantic vector embeddings.

---

# Vector Database

## FAISS (Facebook AI Similarity Search)

Stores and retrieves embeddings for semantic code search.

Responsibilities:

- Fast similarity search
- Code retrieval
- Vector indexing

---

# Repository Processing

Python Standard Library

Libraries:

- os
- pathlib
- shutil
- zipfile

Responsibilities:

- Traverse directories
- Extract ZIP archives
- Read repository structure
- File discovery

---

# Source Code Parsing

Tree-sitter (planned)

or

Python AST

Purpose:

Understand programming language syntax.

Capabilities:

- Function extraction
- Class extraction
- Imports
- Methods
- Metadata

---

# Text Chunking

LangChain Text Splitters

Chunks code into meaningful sections while preserving logical structure.

---

# Prompt Engineering

Custom Prompt Templates

Designed to ensure that the LLM:

- Answers only using retrieved code
- Explains concepts clearly
- Identifies uncertainty
- Avoids unsupported assumptions

---

# Environment Variables

## python-dotenv

Used for securely storing API keys and configuration.

---

# API Testing

## Postman

Used during development for endpoint testing and debugging.

---

# Version Control

## Git

Tracks source code changes.

## GitHub

Repository hosting, collaboration, and portfolio showcase.

---

# Development Environment

Recommended IDE:

- Visual Studio Code

Recommended Extensions:

- Python
- Pylance
- GitLens
- Error Lens
- Black Formatter

---

# Deployment

Backend:

- Render
- Railway

Frontend:

- Streamlit Community Cloud

Future Deployment:

- Docker
- Kubernetes

---

# Project Architecture

```
Repository Upload
        │
        ▼
Repository Scanner
        │
        ▼
File Filtering
        │
        ▼
Code Parsing
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
FAISS Vector Store
        │
        ▼
Retriever
        │
        ▼
LangChain
        │
        ▼
Gemini API
        │
        ▼
AI Response
        │
        ▼
Frontend
```

---

# Primary Python Libraries

- fastapi
- uvicorn
- langchain
- langchain-community
- langchain-google-genai
- google-generativeai
- faiss-cpu
- sentence-transformers
- python-dotenv
- tree-sitter (planned)
- GitPython
- pydantic
- numpy
- pandas
- streamlit

---

# Skills Demonstrated

This project demonstrates practical experience with:

- Python Development
- FastAPI
- REST API Design
- Generative AI
- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- Semantic Code Search
- Prompt Engineering
- LangChain
- Vector Databases
- Embeddings
- Repository Analysis
- AI-assisted Software Engineering
- API Integration
- Git & GitHub
- Production-ready AI Application Development