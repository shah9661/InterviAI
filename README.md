# InterviAI — AI-Powered Personalized Interview & Assessment System

An AI-powered interview platform using **RAG, LLMs, pgVector, LangGraph, and Speech-to-Text** to generate personalized interview questions and evaluate candidate responses.

## Architecture

```text
                         ┌──────────────────────┐
                         │        Html          │
                         │   Interview Client   │
                         └──────────┬───────────┘
                                    │
                                  Voice Answer
                                    │
                                  Audio
                                    │
                                    ▼
                              ┌─────────────┐
                              │ Speech-to-  │
                              │    Text     │
                              └──────┬──────┘
                                     │
                                Transcript
                                     │
                                     |
                                     ▼
                             ┌─────────────┐
                             │   FastAPI   │
                             │ API Gateway │
                             └──────┬──────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
       Authentication          PostgreSQL              Workers
       JWT + Security          + pgVector          Async Processing
                                    │
                                    ▼
                              ┌────────────┐
                              │  RAG Layer │
                              └─────┬──────┘
                                    │
                              Top-K Resume
                                Chunks
                                    │
                                    ▼
                              ┌────────────┐
                              │ LangGraph  │
                              │  Workflow  │
                              └─────┬──────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                    RAG Context             LLM
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                              Evaluation
                                    │
                                    ▼
                            Overall Report
```
## Core Data Model
```
Candidate
   │
   ├── ResumeChunk
   │       └── Embedding
   │
   └── InterviewSession
           │
           ├── Question
           │      └── Answer
           │             └── Evaluation
           │
           └── OverallReport
```
## Resume Processing Pipeline
```
PDF / DOCX
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Chunking
    ↓
Embedding Model
(all-MiniLM-L6-v2)
    ↓
384-Dimensional Vector
    ↓
PostgreSQL + pgVector
```
## Voice Interview Pipeline
```
Microphone
    ↓
Audio
    ↓
Speech-to-Text
    ↓
Transcript
    ↓
Answer
    ↓
Evaluation Pipeline
    ↓
LLM Evaluation
```
## AI Evaluation Pipeline
```
Candidate Answer
       ↓
Question
       ↓
Vector Search
       ↓
Top-K Resume Chunks
       ↓
RAG Context
       ↓
LangGraph
       ↓
LLM
       ↓
Score + Feedback
       ↓
Overall Report
```
## Project Structure
```
InterviAI/
│
├── backend/
│   └── app/
│       ├── api/              # REST API endpoints
│       ├── core/             # Configuration, security & logging
│       ├── db/               # Database, models & repositories
│       ├── schemas/          # Pydantic schemas
│       ├── services/         # Application business logic
│       ├── ai/
│       │   ├── llm/          # LLM integration & prompts
│       │   ├── rag/          # Chunking, embeddings & retrieval
│       │   ├── speech/       # Speech-to-text processing
│       │   └── workflows/    # LangGraph AI workflows
│       ├── workers/          # Asynchronous ML jobs
│       ├── storage/          # Audio/file storage
│       └── main.py           # FastAPI entry point
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   └── components/
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```
## Tech Stack

- **Frontend:** Html,CSS,JavaScripts
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Vector Search:** pgVector
- **LLM:** LLM API
- **Embeddings:** Sentence Transformers
- **RAG:** Custom Retrieval + pgVector
- **AI Workflow:** LangGraph
- **Speech:** Speech-to-Text
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Containerization:** Docker
- **Async Processing:** Background Workers

## Key Features

- 🔐 JWT Authentication
- 📄 Resume PDF/DOCX Processing
- 🧩 Resume Chunking & Embeddings
- 🔎 pgVector Semantic Search
- 🤖 Personalized Question Generation
- 🎤 Voice-Based Interviews
- 🧠 RAG-Based Evaluation
- 📊 AI Interview Reports
- ⚙️ Asynchronous Processing
- 📝 Model & Prompt Versioning
- 📈 Logging & Monitoring
